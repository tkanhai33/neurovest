from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from backend.app.stacks.risk.portfolio_equity import (
    PortfolioEquityUnavailable,
    verify_portfolio_equity,
)


NOW = datetime(
    2026, 10, 13, 22, 50,
    tzinfo=timezone.utc,
)


def quote(
    symbol="AAPL",
    price="300",
    currency="USD",
    observed_at=NOW,
    status="ok",
    provider="fixture",
):
    return {
        "symbol": symbol,
        "price": price,
        "currency": currency,
        "observed_at": observed_at,
        "status": status,
        "provider": provider,
    }


_DEFAULT = object()


def evaluate(
    *,
    cash="100",
    currency="USD",
    positions=_DEFAULT,
    quotes=_DEFAULT,
):
    if positions is _DEFAULT:
        positions = [
            {"symbol": "AAPL", "shares_quantity": "2"}
        ]

    if quotes is _DEFAULT:
        quotes = {"AAPL": quote()}

    return verify_portfolio_equity(
        cash=cash,
        currency=currency,
        positions=positions,
        quotes=quotes,
        now=NOW,
    )


def test_cash_plus_marked_holdings():
    result = evaluate()
    assert result["status"] == "verified"
    assert Decimal(result["net_liquidation_value"]) == 700
    assert Decimal(result["gross_long_exposure"]) == 600
    assert result["risk_limits_enforced"] is False
    assert result["live_execution_allowed"] is False


def test_empty_portfolio_is_cash_only():
    result = evaluate(positions=[], quotes={})
    assert Decimal(result["net_liquidation_value"]) == 100
    assert result["marked_position_count"] == 0


@pytest.mark.parametrize(
    "invalid",
    [None, "-1", "NaN", "Infinity", True, "garbage"],
)
def test_invalid_cash_rejected(invalid):
    with pytest.raises(PortfolioEquityUnavailable):
        evaluate(cash=invalid)


@pytest.mark.parametrize(
    "invalid",
    [None, "0", "-20", "NaN", "Infinity", True],
)
def test_bad_quote_price_rejected(invalid):
    with pytest.raises(PortfolioEquityUnavailable):
        evaluate(quotes={"AAPL": quote(price=invalid)})


@pytest.mark.parametrize(
    "invalid",
    [None, "", "UNKNOWN", "usd-dollar", 123],
)
def test_missing_or_invalid_currency_rejected(invalid):
    with pytest.raises(PortfolioEquityUnavailable):
        evaluate(currency=invalid)


def test_cross_currency_rejected():
    with pytest.raises(
        PortfolioEquityUnavailable,
        match="currency_conversion_unavailable",
    ):
        evaluate(quotes={
            "AAPL": quote(currency="CAD")
        })


def test_stale_quote_rejected():
    old = NOW - timedelta(seconds=301)
    with pytest.raises(
        PortfolioEquityUnavailable,
        match="quote_outside_freshness_policy",
    ):
        evaluate(quotes={
            "AAPL": quote(observed_at=old)
        })


def test_future_quote_rejected():
    future = NOW + timedelta(seconds=1)
    with pytest.raises(PortfolioEquityUnavailable):
        evaluate(quotes={
            "AAPL": quote(observed_at=future)
        })


def test_missing_timestamp_rejected():
    with pytest.raises(PortfolioEquityUnavailable):
        evaluate(quotes={
            "AAPL": quote(observed_at=None)
        })


def test_naive_timestamp_rejected():
    with pytest.raises(PortfolioEquityUnavailable):
        evaluate(quotes={
            "AAPL": quote(
                observed_at=NOW.replace(tzinfo=None)
            )
        })


def test_missing_symbol_quote_rejected():
    with pytest.raises(PortfolioEquityUnavailable):
        evaluate(quotes={})


def test_quote_symbol_mismatch_rejected():
    with pytest.raises(PortfolioEquityUnavailable):
        evaluate(quotes={
            "AAPL": quote(symbol="MSFT")
        })


def test_bad_quote_status_rejected():
    with pytest.raises(PortfolioEquityUnavailable):
        evaluate(quotes={
            "AAPL": quote(status="error")
        })


def test_missing_quote_provider_rejected():
    with pytest.raises(PortfolioEquityUnavailable):
        evaluate(quotes={
            "AAPL": quote(provider="")
        })


def test_duplicate_positions_rejected():
    with pytest.raises(PortfolioEquityUnavailable):
        evaluate(positions=[
            {"symbol": "AAPL", "shares_quantity": "1"},
            {"symbol": "aapl", "shares_quantity": "1"},
        ])


def test_bad_quantity_rejected():
    with pytest.raises(PortfolioEquityUnavailable):
        evaluate(positions=[
            {"symbol": "AAPL", "shares_quantity": "-2"}
        ])


def test_multiple_positions():
    result = evaluate(
        positions=[
            {"symbol": "AAPL", "shares_quantity": "2"},
            {"symbol": "MSFT", "shares_quantity": "3"},
        ],
        quotes={
            "AAPL": quote(),
            "MSFT": quote(symbol="MSFT", price="200"),
        },
    )
    assert Decimal(result["net_liquidation_value"]) == 1300
    assert result["marked_position_count"] == 2


def test_zero_position_requires_no_quote():
    result = evaluate(
        positions=[
            {"symbol": "AAPL", "shares_quantity": "0"}
        ],
        quotes={},
    )
    assert Decimal(result["net_liquidation_value"]) == 100


def test_missing_owner_data_is_not_invented():
    with pytest.raises(PortfolioEquityUnavailable):
        evaluate(positions=None, quotes={"AAPL": quote()})
