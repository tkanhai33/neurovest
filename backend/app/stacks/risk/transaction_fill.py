"""Fail-closed validation for long-only paper fills.

Pure Decimal arithmetic. No database access, order submission,
or execution authorization.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation


class PaperFillUnavailable(ValueError):
    pass


def _number(value, name, *, positive=False):
    if value is None or isinstance(value, bool):
        raise PaperFillUnavailable(f"{name}_unavailable")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError, OverflowError):
        raise PaperFillUnavailable(f"{name}_invalid") from None
    if not result.is_finite() or result < 0:
        raise PaperFillUnavailable(f"{name}_invalid")
    if positive and result <= 0:
        raise PaperFillUnavailable(f"{name}_invalid")
    return result


def _symbol(value):
    if not isinstance(value, str) or not value.strip():
        raise PaperFillUnavailable("symbol_invalid")
    normalized = value.strip().upper()
    if not normalized.isascii():
        raise PaperFillUnavailable("symbol_invalid")
    return normalized


def _currency(value):
    if not isinstance(value, str):
        raise PaperFillUnavailable("currency_unavailable")
    code = value.strip().upper()
    if len(code) != 3 or not code.isascii() or not code.isalpha():
        raise PaperFillUnavailable("currency_invalid")
    return code


def _time(value, name):
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise PaperFillUnavailable(f"{name}_invalid")
    return value.astimezone(timezone.utc)


def validate_transaction_fill(
    *,
    symbol: str,
    action: str,
    allocated_capital: object,
    fill_price: object,
    commission: object,
    account_currency: str,
    execution_quote: Mapping,
    positions: Sequence[Mapping],
    now: datetime,
    max_quote_age_seconds: int = 300,
    max_slippage_bps: object = "50",
) -> dict:
    name = _symbol(symbol)

    if not isinstance(action, str):
        raise PaperFillUnavailable("action_invalid")
    side = action.strip().lower()
    if side not in ("buy", "sell"):
        raise PaperFillUnavailable("action_invalid")

    value = _number(allocated_capital, "allocated_capital", positive=True)
    price = _number(fill_price, "fill_price", positive=True)
    fee = _number(commission, "commission")
    account = _currency(account_currency)
    tolerance = _number(max_slippage_bps, "max_slippage_bps")

    if tolerance > Decimal("10000"):
        raise PaperFillUnavailable("max_slippage_bps_invalid")

    if (
        isinstance(max_quote_age_seconds, bool)
        or not isinstance(max_quote_age_seconds, int)
        or max_quote_age_seconds <= 0
    ):
        raise PaperFillUnavailable("quote_age_policy_invalid")

    checked = _time(now, "verification_time")

    if not isinstance(execution_quote, Mapping):
        raise PaperFillUnavailable("execution_quote_unavailable")
    if execution_quote.get("status") != "ok":
        raise PaperFillUnavailable("execution_quote_not_ok")
    if _symbol(execution_quote.get("symbol")) != name:
        raise PaperFillUnavailable("execution_quote_symbol_mismatch")
    if _currency(execution_quote.get("currency")) != account:
        raise PaperFillUnavailable("execution_currency_mismatch")

    provider = execution_quote.get("provider")
    if not isinstance(provider, str) or not provider.strip():
        raise PaperFillUnavailable("execution_provider_unavailable")

    observed = _time(
        execution_quote.get("observed_at"),
        "execution_observed_at",
    )
    age = checked - observed
    if age < timedelta(0) or age > timedelta(
        seconds=max_quote_age_seconds
    ):
        raise PaperFillUnavailable("execution_quote_stale_or_future")

    reference = _number(
        execution_quote.get("price"),
        "execution_reference_price",
        positive=True,
    )
    slippage_bps = (
        abs(price - reference) / reference * Decimal("10000")
    )
    if slippage_bps > tolerance:
        raise PaperFillUnavailable("execution_price_deviation_exceeded")

    if not isinstance(positions, (list, tuple)):
        raise PaperFillUnavailable("inventory_unavailable")

    owned = Decimal("0")
    seen = set()
    for position in positions:
        if not isinstance(position, Mapping):
            raise PaperFillUnavailable("inventory_position_invalid")
        position_symbol = _symbol(position.get("symbol"))
        if position_symbol in seen:
            raise PaperFillUnavailable("duplicate_inventory_symbol")
        seen.add(position_symbol)
        quantity = _number(
            position.get("shares_quantity"),
            "inventory_quantity",
        )
        if position_symbol == name:
            owned = quantity

    shares = value / price
    if side == "sell" and shares > owned:
        raise PaperFillUnavailable(
            "sell_shares_exceed_symbol_inventory"
        )

    return {
        "status": "validated",
        "symbol": name,
        "action": side,
        "allocated_capital": str(value),
        "fill_price": str(price),
        "reference_price": str(reference),
        "commission": str(fee),
        "shares_filled": str(shares),
        "symbol_shares_available": str(owned),
        "slippage_bps": str(slippage_bps),
        "currency": account,
        "provider": provider.strip(),
        "observed_at": observed.isoformat(),
        "execution_authorized": False,
        "transaction_consistent": False,
    }
