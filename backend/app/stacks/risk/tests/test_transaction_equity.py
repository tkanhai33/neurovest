from __future__ import annotations

from unittest.mock import AsyncMock
from datetime import datetime, timezone

import pytest

import backend.app.stacks.risk.transaction_equity as target
from backend.app.stacks.risk.transaction_equity import (
    TransactionEquityUnavailable,
)


class Session:
    def in_transaction(self):
        return True


@pytest.fixture
def sources(monkeypatch):
    cash = AsyncMock(return_value={
        "user_id": "owner-1",
        "scope": "caller_database_session",
        "current_cash_balance": "8000",
    })
    inventory = AsyncMock(return_value=[
        {
            "symbol": "AAPL",
            "shares_quantity": "2",
            "total_cost_basis": "200",
            "average_entry_price": "100",
        }
    ])

    observed = {}

    def verify(**kwargs):
        observed.update(kwargs)
        return {
            "status": "verified",
            "cash": "8000",
            "gross_long_exposure": "200",
            "net_liquidation_value": "8200",
            "risk_limits_enforced": False,
        }

    monkeypatch.setattr(target, "calculate_cash_in_session", cash)
    monkeypatch.setattr(target, "read_inventory_in_session", inventory)
    monkeypatch.setattr(target, "verify_portfolio_equity", verify)

    return cash, inventory, observed


async def run(*, session=None, owner="owner-1",
              currency="USD", quote_loader=None):
    if session is None:
        session = Session()

    if quote_loader is None:
        quote_loader = AsyncMock(return_value={
            "status": "ok",
            "symbol": "AAPL",
            "price": "100",
            "currency": "USD",
            "observed_at": datetime(
                2026, 10, 13, 21, 0, tzinfo=timezone.utc
            ),
        })

    return await target.read_transaction_verified_equity(
        session=session,
        user_id=owner,
        cash_currency=currency,
        quote_loader=quote_loader,
        now=datetime(2026, 10, 13, 21, 1, tzinfo=timezone.utc),
    )


async def test_same_session_and_owner_used(sources):
    cash, inventory, observed = sources
    session = Session()

    result = await run(session=session)

    assert result["status"] == "verified"
    assert result["execution_authorized"] is False
    assert result["transaction_consistent"] is False
    assert cash.await_args.kwargs["session"] is session
    assert inventory.await_args.kwargs["session"] is session
    assert cash.await_args.kwargs["user_id"] == "owner-1"
    assert inventory.await_args.kwargs["user_id"] == "owner-1"
    assert observed["cash"] == "8000"
    assert observed["currency"] == "USD"


async def test_quotes_forwarded_without_fabrication(sources):
    _, _, observed = sources

    loader = AsyncMock(return_value={
        "status": "ok",
        "symbol": "AAPL",
        "price": "99",
    })
    await run(quote_loader=loader)

    assert "observed_at" not in observed["quotes"]["AAPL"]
    assert "currency" not in observed["quotes"]["AAPL"]
    loader.assert_awaited_once_with("AAPL")


async def test_invalid_owner_fails_before_queries(sources):
    cash, inventory, _ = sources

    with pytest.raises(TransactionEquityUnavailable):
        await run(owner=" ")

    cash.assert_not_awaited()
    inventory.assert_not_awaited()


async def test_missing_currency_fails_closed(sources):
    with pytest.raises(TransactionEquityUnavailable):
        await run(currency="")


async def test_unverified_cash_owner_fails_closed(sources):
    cash, _, _ = sources
    cash.return_value["user_id"] = "other"

    with pytest.raises(
        TransactionEquityUnavailable,
        match="cash_owner_mismatch",
    ):
        await run()


async def test_missing_transaction_fails_closed(sources):
    class NoTransaction:
        def in_transaction(self):
            return False

    with pytest.raises(
        TransactionEquityUnavailable,
        match="transaction_required",
    ):
        await run(session=NoTransaction())


async def test_no_positions_does_not_request_quote(sources):
    _, inventory, observed = sources
    inventory.return_value = []
    loader = AsyncMock()

    await run(quote_loader=loader)

    assert observed["positions"] == []
    loader.assert_not_awaited()


async def test_quote_loader_failure_blocks(sources):
    loader = AsyncMock(side_effect=RuntimeError("market unavailable"))

    with pytest.raises(RuntimeError, match="market unavailable"):
        await run(quote_loader=loader)


async def test_unverified_valuation_blocks(sources, monkeypatch):
    monkeypatch.setattr(
        target,
        "verify_portfolio_equity",
        lambda **kwargs: {"status": "unavailable"},
    )
    with pytest.raises(
        TransactionEquityUnavailable,
        match="valuation_not_verified",
    ):
        await run()


async def test_cash_reader_error_propagates(sources):
    cash, _, _ = sources
    cash.side_effect = ValueError("unreconciled history")

    with pytest.raises(ValueError, match="unreconciled history"):
        await run()
