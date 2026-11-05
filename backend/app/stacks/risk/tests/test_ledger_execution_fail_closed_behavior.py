from __future__ import annotations

from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

import backend.app.stacks.journal_ledger.ledger as ledger
import backend.app.stacks.portfolio.accounting as accounting
import backend.app.stacks.execution.execution_control as control_module
import backend.app.stacks.risk.transaction_equity as equity_module


class FakeResult:
    def __init__(self, *, rows=(), scalar_rows=()):
        self.rows = list(rows)
        self.scalar_rows = list(scalar_rows)

    def mappings(self):
        return self

    def first(self):
        return self.rows[0] if self.rows else None

    def scalars(self):
        return FakeResult(rows=self.scalar_rows)

    def all(self):
        return self.rows


class FakeSession:
    def __init__(self, *, currency_rows=(), existing=None):
        self.currency_rows = list(currency_rows)
        self.existing = existing
        self.queries = []
        self.added = []
        self.flushed = False
        self.committed = False
        self.rolled_back = False

    @asynccontextmanager
    async def begin(self):
        try:
            yield
        except BaseException:
            self.rolled_back = True
            raise
        else:
            self.committed = True

    async def execute(self, statement, params=None):
        sql = str(statement)
        self.queries.append(sql)

        if "pg_advisory_xact_lock" in sql:
            return FakeResult()
        if "FROM order_history" in sql and "request_id" in sql:
            return FakeResult(
                rows=[self.existing] if self.existing else []
            )
        if "FROM paper_equity_high_water" in sql:
            return FakeResult(scalar_rows=self.currency_rows)

        raise AssertionError("unexpected SQL: " + sql)

    def add(self, obj):
        self.added.append(obj)

    async def flush(self):
        self.flushed = True


def install(monkeypatch, session):
    @asynccontextmanager
    async def session_factory():
        yield session

    monkeypatch.setattr(ledger, "async_session", session_factory)

    monkeypatch.setattr(
        control_module.execution_control,
        "assert_paper_execution_allowed",
        lambda: None,
    )

    cash = AsyncMock(return_value={
        "user_id": "owner-A",
        "scope": "caller_database_session",
        "current_cash_balance": "8000",
    })

    positions = AsyncMock(return_value=[])

    monkeypatch.setattr(accounting, "calculate_cash_in_session", cash)
    monkeypatch.setattr(ledger, "read_inventory_in_session", positions)

    return cash, positions


TRADE = {
    "symbol": "AAPL",
    "signal": "buy",
    "status": "executed",
    "allocated_capital": "500",
    "slippage_price": "100",
    "commission_paid": "1",
}


async def test_missing_currency_rolls_back_without_order_write(
    monkeypatch,
):
    session = FakeSession(currency_rows=[])
    cash, positions = install(monkeypatch, session)

    with pytest.raises(
        RuntimeError, match="paper_account_currency_unverified"
    ):
        await ledger.save_log(TRADE, user_id="owner-A")

    cash.assert_awaited_once()
    positions.assert_awaited_once()
    assert session.rolled_back is True
    assert session.committed is False
    assert session.added == []
    assert session.flushed is False


async def test_unverified_valuation_rolls_back_without_order_write(
    monkeypatch,
):
    session = FakeSession(currency_rows=["USD"])
    install(monkeypatch, session)

    valuation = AsyncMock(
        side_effect=RuntimeError("quote_timestamp_unverified")
    )
    monkeypatch.setattr(
        equity_module, "read_transaction_verified_equity", valuation
    )

    with pytest.raises(
        RuntimeError, match="quote_timestamp_unverified"
    ):
        await ledger.save_log(TRADE, user_id="owner-A")

    valuation.assert_awaited_once()
    assert valuation.await_args.kwargs["session"] is session
    assert valuation.await_args.kwargs["user_id"] == "owner-A"
    assert session.rolled_back is True
    assert session.committed is False
    assert session.added == []
    assert session.flushed is False


async def test_blockade_cannot_be_bypassed_by_valid_policy(
    monkeypatch,
):
    session = FakeSession(currency_rows=["USD"])
    install(monkeypatch, session)

    valuation = AsyncMock(return_value={
        "status": "verified",
        "owner": "owner-A",
        "execution_authorized": False,
        "cash": "8000",
        "gross_long_exposure": "2000",
        "net_liquidation_value": "10000",
        "risk_limits_enforced": False,
        "marked_position_count": 0,
        "marks": [],
    })
    monkeypatch.setattr(
        equity_module, "read_transaction_verified_equity", valuation
    )

    import backend.app.stacks.risk.transactional_policy as policy

    decision = AsyncMock(return_value={
        "approved": True,
        "execution_authorized": False,
    })
    monkeypatch.setattr(
        policy, "evaluate_transactional_financial_policy", decision
    )

    import backend.app.stacks.market_data.risk_valuation_quotes as quotes
    from datetime import datetime, timezone

    quote_loader = AsyncMock(side_effect=lambda requested_symbol: {
        "status": "ok",
        "symbol": requested_symbol,
        "price": TRADE["slippage_price"],
        "currency": "USD",
        "observed_at": datetime.now(timezone.utc),
        "provider": "yfinance",
    })

    monkeypatch.setattr(
        quotes,
        "get_risk_valuation_quote",
        quote_loader,
    )

    for name, value in {
        "NEUROVEST_PAPER_MAX_ORDER_VALUE": "1000",
        "NEUROVEST_PAPER_MAX_GROSS_EXPOSURE": "5000",
        "NEUROVEST_PAPER_MAX_DRAWDOWN_FRACTION": "0.20",
        "NEUROVEST_PAPER_MAX_SLIPPAGE_BPS": "50",
    }.items():
        monkeypatch.setenv(name, value)

    with pytest.raises(
        RuntimeError,
        match="paper_execution_financial_risk_not_qualified",
    ):
        await ledger.save_log(TRADE, user_id="owner-A")

    quote_loader.assert_awaited_once()
    decision.assert_awaited_once()
    assert decision.await_args.kwargs["session"] is session
    assert session.rolled_back is True
    assert session.committed is False
    assert session.added == []
    assert session.flushed is False
