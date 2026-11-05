from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from backend.app.stacks.market_data.risk_valuation_quotes import (
    RiskQuoteUnavailable,
    get_risk_valuation_quote,
    normalize_risk_bar_quote,
)
from backend.app.stacks.risk.portfolio_equity import (
    PortfolioEquityUnavailable,
    verify_portfolio_equity,
)


NOW = datetime(2026, 10, 13, 18, 30, tzinfo=timezone.utc)


def payload(**changes):
    result = {
        "symbol": "AAPL",
        "price": "200.25",
        "currency": "USD",
        "observed_at": NOW - timedelta(seconds=30),
        "provider": "yfinance",
    }
    result.update(changes)
    return result


def value_quote(p):
    return verify_portfolio_equity(
        cash="5000",
        currency="USD",
        positions=[
            {"symbol": "AAPL", "shares_quantity": "2"}
        ],
        quotes={"AAPL": p},
        now=NOW,
        max_quote_age_seconds=300,
    )


def test_good_source_quote_reconciles_equity():
    quote = normalize_risk_bar_quote("AAPL", payload())
    value = value_quote(quote)
    assert value["status"] == "verified"
    assert value["net_liquidation_value"] == "5400.50"
    assert value["live_execution_allowed"] is False


@pytest.mark.parametrize("bad", [
    None, "", "unknown", "US", "USDD", 123,
])
def test_missing_currency_rejected(bad):
    with pytest.raises(RiskQuoteUnavailable):
        normalize_risk_bar_quote(
            "AAPL", payload(currency=bad)
        )


@pytest.mark.parametrize("bad", [
    None,
    "",
    "now",
    1791920000,
    NOW.replace(tzinfo=None),
])
def test_timestamp_not_invented(bad):
    with pytest.raises(RiskQuoteUnavailable):
        normalize_risk_bar_quote(
            "AAPL", payload(observed_at=bad)
        )


@pytest.mark.parametrize("bad", [
    None, 0, -1, "NaN", "Infinity", True,
])
def test_invalid_price_rejected(bad):
    with pytest.raises(RiskQuoteUnavailable):
        normalize_risk_bar_quote(
            "AAPL", payload(price=bad)
        )


def test_provider_identity_required():
    with pytest.raises(RiskQuoteUnavailable):
        normalize_risk_bar_quote(
            "AAPL", payload(provider=None)
        )


def test_symbol_mismatch_rejected():
    with pytest.raises(RiskQuoteUnavailable):
        normalize_risk_bar_quote(
            "AAPL", payload(symbol="MSFT")
        )


def test_stale_source_bar_rejected_by_equity_verifier():
    quote = normalize_risk_bar_quote(
        "AAPL",
        payload(
            observed_at=NOW - timedelta(minutes=10)
        ),
    )
    with pytest.raises(
        PortfolioEquityUnavailable,
        match="quote_outside_freshness_policy",
    ):
        value_quote(quote)


def test_future_source_bar_rejected_by_equity_verifier():
    quote = normalize_risk_bar_quote(
        "AAPL",
        payload(
            observed_at=NOW + timedelta(seconds=10)
        ),
    )
    with pytest.raises(
        PortfolioEquityUnavailable,
        match="quote_outside_freshness_policy",
    ):
        value_quote(quote)


def test_cross_currency_rejected_by_equity_verifier():
    quote = normalize_risk_bar_quote(
        "AAPL", payload(currency="CAD")
    )
    with pytest.raises(
        PortfolioEquityUnavailable,
        match="currency_conversion_unavailable",
    ):
        value_quote(quote)


async def test_async_adapter_uses_source_timestamp():
    calls = []

    def fixture_fetch(symbol):
        calls.append(symbol)
        return payload()

    quote = await get_risk_valuation_quote(
        " aapl ",
        source_loader=fixture_fetch,
    )

    assert calls == ["AAPL"]
    assert quote["observed_at"] == (
        NOW - timedelta(seconds=30)
    )
    assert quote["price"] == "200.25"


async def test_async_adapter_fails_on_missing_source_time():
    def fixture_fetch(symbol):
        result = payload()
        del result["observed_at"]
        return result

    with pytest.raises(
        RiskQuoteUnavailable,
        match="source_bar_timestamp_unavailable",
    ):
        await get_risk_valuation_quote(
            "AAPL",
            source_loader=fixture_fetch,
        )


async def test_async_adapter_rejects_non_callable_source():
    with pytest.raises(
        RiskQuoteUnavailable,
        match="source_loader_invalid",
    ):
        await get_risk_valuation_quote(
            "AAPL",
            source_loader="not_callable",
        )
