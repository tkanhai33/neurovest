from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from backend.app.stacks.risk.transaction_fill import (
    PaperFillUnavailable,
    validate_transaction_fill,
)

NOW = datetime(2026, 10, 13, 19, 0, tzinfo=timezone.utc)
QUOTE = {
    "status": "ok",
    "symbol": "AAPL",
    "price": "100",
    "currency": "USD",
    "provider": "yfinance",
    "observed_at": NOW - timedelta(seconds=30),
}
INVENTORY = [
    {"symbol": "AAPL", "shares_quantity": "5"},
    {"symbol": "MSFT", "shares_quantity": "100"},
]


def check(**changes):
    kwargs = {
        "symbol": "AAPL",
        "action": "buy",
        "allocated_capital": "200",
        "fill_price": "100.20",
        "commission": "1",
        "account_currency": "USD",
        "execution_quote": QUOTE,
        "positions": INVENTORY,
        "now": NOW,
        "max_slippage_bps": "50",
    }
    kwargs.update(changes)
    return validate_transaction_fill(**kwargs)


def test_valid_buy_exact_decimal_shares():
    result = check()
    assert Decimal(result["shares_filled"]) == (
        Decimal("200") / Decimal("100.20")
    )
    assert result["execution_authorized"] is False


def test_valid_sell():
    result = check(
        action="sell", allocated_capital="400", fill_price="100"
    )
    assert result["shares_filled"] == "4"


def test_sell_exact_inventory():
    result = check(
        action="sell", allocated_capital="500", fill_price="100"
    )
    assert result["shares_filled"] == "5"


def test_sell_exceeding_symbol_inventory():
    with pytest.raises(
        PaperFillUnavailable,
        match="sell_shares_exceed_symbol_inventory",
    ):
        check(
            action="sell",
            allocated_capital="600",
            fill_price="100",
        )


def test_other_symbol_cannot_cover_sell():
    with pytest.raises(
        PaperFillUnavailable,
        match="sell_shares_exceed_symbol_inventory",
    ):
        check(
            action="sell",
            positions=[{"symbol": "MSFT", "shares_quantity": "100"}],
        )


@pytest.mark.parametrize(
    "price", ["0", "-1", "NaN", "Infinity", None, True]
)
def test_invalid_fill_price(price):
    with pytest.raises(PaperFillUnavailable):
        check(fill_price=price)


@pytest.mark.parametrize(
    "value", ["0", "-5", "NaN", "Infinity", None]
)
def test_invalid_capital(value):
    with pytest.raises(PaperFillUnavailable):
        check(allocated_capital=value)


@pytest.mark.parametrize("fee", ["-1", "NaN", None])
def test_invalid_commission(fee):
    with pytest.raises(PaperFillUnavailable):
        check(commission=fee)


def test_excessive_slippage():
    with pytest.raises(
        PaperFillUnavailable,
        match="execution_price_deviation_exceeded",
    ):
        check(fill_price="105")


def test_slippage_boundary():
    assert Decimal(check(fill_price="100.50")["slippage_bps"]) == 50


@pytest.mark.parametrize("seconds", [-10, 600])
def test_future_or_stale_quote(seconds):
    with pytest.raises(
        PaperFillUnavailable,
        match="execution_quote_stale_or_future",
    ):
        check(
            execution_quote={
                **QUOTE,
                "observed_at": NOW - timedelta(seconds=seconds),
            }
        )


def test_missing_timestamp():
    with pytest.raises(PaperFillUnavailable):
        check(execution_quote={**QUOTE, "observed_at": None})


def test_currency_mismatch():
    with pytest.raises(
        PaperFillUnavailable,
        match="execution_currency_mismatch",
    ):
        check(execution_quote={**QUOTE, "currency": "CAD"})


def test_symbol_mismatch():
    with pytest.raises(
        PaperFillUnavailable,
        match="execution_quote_symbol_mismatch",
    ):
        check(execution_quote={**QUOTE, "symbol": "MSFT"})


def test_missing_reference_price():
    with pytest.raises(PaperFillUnavailable):
        check(execution_quote={**QUOTE, "price": None})


def test_duplicate_inventory():
    with pytest.raises(
        PaperFillUnavailable,
        match="duplicate_inventory_symbol",
    ):
        check(positions=INVENTORY + INVENTORY[:1])


def test_short_selling_unsupported():
    with pytest.raises(PaperFillUnavailable, match="action_invalid"):
        check(action="short")


def test_missing_quote():
    with pytest.raises(
        PaperFillUnavailable,
        match="execution_quote_unavailable",
    ):
        check(execution_quote=None)
