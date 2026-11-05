from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

import backend.app.stacks.risk.portfolio_equity_adapter as adapter
from backend.app.stacks.risk.portfolio_equity import (
    PortfolioEquityUnavailable,
)


NOW = datetime(2026, 10, 13, 22, 55, tzinfo=timezone.utc)


def set_ledger(monkeypatch, cash="100", positions=None):
    if positions is None:
        positions = [
            {"symbol": "AAPL", "shares_quantity": "2"}
        ]

    cash_read = AsyncMock(return_value={
        "current_cash_balance": cash,
    })
    positions_read = AsyncMock(return_value=positions)

    monkeypatch.setattr(
        adapter,
        "calculate_live_portfolio_equity",
        cash_read,
    )
    monkeypatch.setattr(
        adapter,
        "read_portfolio_positions",
        positions_read,
    )

    return cash_read, positions_read


def valid_quote(symbol):
    return {
        "status": "ok",
        "symbol": symbol,
        "price": "300",
        "currency": "USD",
        "observed_at": NOW,
        "provider": "fixture",
    }


async def test_owner_propagation_and_equity(monkeypatch):
    cash_read, positions_read = set_ledger(monkeypatch)
    loader = AsyncMock(side_effect=valid_quote)

    result = await adapter.read_verified_owner_equity(
        user_id=" owner-1 ",
        cash_currency="USD",
        quote_loader=loader,
        now=NOW,
    )

    cash_read.assert_awaited_once_with(user_id="owner-1")
    positions_read.assert_awaited_once_with(user_id="owner-1")
    loader.assert_awaited_once_with("AAPL")

    assert Decimal(result["net_liquidation_value"]) == 700
    assert result["valuation_scope"] == "owner_scoped_non_atomic"
    assert result["execution_approval"] is False


async def test_empty_inventory_needs_no_quotes(monkeypatch):
    set_ledger(monkeypatch, positions=[])
    loader = AsyncMock(side_effect=AssertionError("must not call"))

    result = await adapter.read_verified_owner_equity(
        user_id="owner-1",
        cash_currency="USD",
        quote_loader=loader,
        now=NOW,
    )

    assert result["net_liquidation_value"] == "100"
    loader.assert_not_awaited()


async def test_missing_owner_fails_before_database(monkeypatch):
    cash_read, _, = set_ledger(monkeypatch)

    with pytest.raises(PortfolioEquityUnavailable):
        await adapter.read_verified_owner_equity(
            user_id=" ",
            cash_currency="USD",
            quote_loader=AsyncMock(),
            now=NOW,
        )

    cash_read.assert_not_awaited()


async def test_ledger_failure_fails_closed(monkeypatch):
    cash_read, _ = set_ledger(monkeypatch)
    cash_read.side_effect = RuntimeError("database down")

    with pytest.raises(
        PortfolioEquityUnavailable,
        match="owner_ledger_unavailable",
    ):
        await adapter.read_verified_owner_equity(
            user_id="owner-1",
            cash_currency="USD",
            quote_loader=AsyncMock(),
            now=NOW,
        )


async def test_quote_failure_fails_closed(monkeypatch):
    set_ledger(monkeypatch)

    with pytest.raises(
        PortfolioEquityUnavailable,
        match="quote_provider_unavailable",
    ):
        await adapter.read_verified_owner_equity(
            user_id="owner-1",
            cash_currency="USD",
            quote_loader=AsyncMock(
                side_effect=RuntimeError("market unavailable")
            ),
            now=NOW,
        )


async def test_missing_observed_at_rejected(monkeypatch):
    set_ledger(monkeypatch)
    value = valid_quote("AAPL")
    value.pop("observed_at")

    with pytest.raises(
        PortfolioEquityUnavailable,
        match="quote_timestamp_unavailable",
    ):
        await adapter.read_verified_owner_equity(
            user_id="owner-1",
            cash_currency="USD",
            quote_loader=AsyncMock(return_value=value),
            now=NOW,
        )


async def test_stale_observation_rejected(monkeypatch):
    set_ledger(monkeypatch)
    value = valid_quote("AAPL")
    value["observed_at"] = NOW - timedelta(seconds=301)

    with pytest.raises(
        PortfolioEquityUnavailable,
        match="quote_outside_freshness_policy",
    ):
        await adapter.read_verified_owner_equity(
            user_id="owner-1",
            cash_currency="USD",
            quote_loader=AsyncMock(return_value=value),
            now=NOW,
        )


async def test_currency_mismatch_rejected(monkeypatch):
    set_ledger(monkeypatch)
    value = valid_quote("AAPL")
    value["currency"] = "CAD"

    with pytest.raises(
        PortfolioEquityUnavailable,
        match="currency_conversion_unavailable",
    ):
        await adapter.read_verified_owner_equity(
            user_id="owner-1",
            cash_currency="USD",
            quote_loader=AsyncMock(return_value=value),
            now=NOW,
        )


async def test_missing_account_currency_rejected(monkeypatch):
    cash_read, _ = set_ledger(monkeypatch)

    with pytest.raises(PortfolioEquityUnavailable):
        await adapter.read_verified_owner_equity(
            user_id="owner-1",
            cash_currency="",
            quote_loader=AsyncMock(),
            now=NOW,
        )

    cash_read.assert_not_awaited()


async def test_duplicate_inventory_symbols_rejected(monkeypatch):
    set_ledger(
        monkeypatch,
        positions=[
            {"symbol": "AAPL", "shares_quantity": "1"},
            {"symbol": "aapl", "shares_quantity": "1"},
        ],
    )

    with pytest.raises(
        PortfolioEquityUnavailable,
        match="duplicate_position_symbol",
    ):
        await adapter.read_verified_owner_equity(
            user_id="owner-1",
            cash_currency="USD",
            quote_loader=AsyncMock(),
            now=NOW,
        )
