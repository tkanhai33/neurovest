"""Recheck original transaction quotes after risk policy.

Pure validation. Does not fetch quotes, persist orders,
or authorize financial execution.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation


class FinalTransactionQuoteUnavailable(ValueError):
    pass


def _symbol(value):
    if (
        not isinstance(value, str)
        or not value.strip()
        or not value.strip().isascii()
    ):
        raise FinalTransactionQuoteUnavailable(
            "final_quote_symbol_invalid"
        )
    return value.strip().upper()


def _currency(value):
    if (
        not isinstance(value, str)
        or len(value) != 3
        or not value.isascii()
        or not value.isalpha()
        or value != value.upper()
    ):
        raise FinalTransactionQuoteUnavailable(
            "final_quote_currency_invalid"
        )
    return value


def _timestamp(value):
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except (ValueError, TypeError, OverflowError):
            raise FinalTransactionQuoteUnavailable(
                "final_quote_timestamp_invalid"
            ) from None

    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise FinalTransactionQuoteUnavailable(
            "final_quote_timestamp_invalid"
        )

    return value.astimezone(timezone.utc)


def _number(value, *, positive):
    if value is None or isinstance(value, bool):
        raise FinalTransactionQuoteUnavailable(
            "final_quote_number_invalid"
        )
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError, OverflowError):
        raise FinalTransactionQuoteUnavailable(
            "final_quote_number_invalid"
        ) from None

    if not number.is_finite():
        raise FinalTransactionQuoteUnavailable(
            "final_quote_number_invalid"
        )

    if number <= 0 if positive else number < 0:
        raise FinalTransactionQuoteUnavailable(
            "final_quote_number_invalid"
        )

    return number


def _verify_quote(quote, expected, currency, now, age_limit):
    if not isinstance(quote, Mapping):
        raise FinalTransactionQuoteUnavailable(
            "final_quote_unavailable"
        )

    if quote.get("status", "ok") != "ok":
        raise FinalTransactionQuoteUnavailable(
            "final_quote_status_invalid"
        )

    if _symbol(quote.get("symbol")) != expected:
        raise FinalTransactionQuoteUnavailable(
            "final_quote_symbol_mismatch"
        )

    if _currency(quote.get("currency")) != currency:
        raise FinalTransactionQuoteUnavailable(
            "final_quote_currency_mismatch"
        )

    provider = quote.get("provider")
    if not isinstance(provider, str) or not provider.strip():
        raise FinalTransactionQuoteUnavailable(
            "final_quote_provider_invalid"
        )

    _number(quote.get("price"), positive=True)
    observed = _timestamp(quote.get("observed_at"))
    age = now - observed

    if age < timedelta(0) or age > timedelta(seconds=age_limit):
        raise FinalTransactionQuoteUnavailable(
            "final_quote_stale_or_future"
        )


def validate_final_transaction_quote_freshness(
    *,
    positions: Sequence[Mapping],
    marks: Sequence[Mapping],
    execution_quote: Mapping,
    symbol: str,
    account_currency: str,
    now: datetime,
    max_quote_age_seconds: int = 300,
) -> dict:
    checked = _timestamp(now)
    currency = _currency(account_currency)
    execution_symbol = _symbol(symbol)

    if (
        isinstance(max_quote_age_seconds, bool)
        or not isinstance(max_quote_age_seconds, int)
        or max_quote_age_seconds <= 0
    ):
        raise FinalTransactionQuoteUnavailable(
            "final_quote_age_policy_invalid"
        )

    if not isinstance(positions, (list, tuple)):
        raise FinalTransactionQuoteUnavailable(
            "final_inventory_unavailable"
        )

    if not isinstance(marks, (list, tuple)):
        raise FinalTransactionQuoteUnavailable(
            "final_marks_unavailable"
        )

    expected = set()
    inventory_seen = set()

    for position in positions:
        if not isinstance(position, Mapping):
            raise FinalTransactionQuoteUnavailable(
                "final_inventory_position_invalid"
            )

        name = _symbol(position.get("symbol"))

        if name in inventory_seen:
            raise FinalTransactionQuoteUnavailable(
                "final_inventory_duplicate_symbol"
            )

        inventory_seen.add(name)

        if _number(
            position.get("shares_quantity"),
            positive=False,
        ) > 0:
            expected.add(name)

    verified = set()

    for mark in marks:
        if not isinstance(mark, Mapping):
            raise FinalTransactionQuoteUnavailable(
                "final_mark_invalid"
            )

        name = _symbol(mark.get("symbol"))

        if name in verified:
            raise FinalTransactionQuoteUnavailable(
                "final_mark_duplicate_symbol"
            )

        verified.add(name)

        if name not in expected:
            raise FinalTransactionQuoteUnavailable(
                "final_mark_unexpected_symbol"
            )

        _verify_quote(
            mark, name, currency, checked,
            max_quote_age_seconds,
        )

    if verified != expected:
        raise FinalTransactionQuoteUnavailable(
            "final_mark_coverage_mismatch"
        )

    _verify_quote(
        execution_quote, execution_symbol, currency,
        checked, max_quote_age_seconds,
    )

    return {
        "status": "validated",
        "marked_position_count": len(verified),
        "execution_symbol": execution_symbol,
        "execution_authorized": False,
        "transaction_consistent": False,
    }
