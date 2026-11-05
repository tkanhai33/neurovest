from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from typing import Mapping, Sequence


class PortfolioEquityUnavailable(ValueError):
    """Portfolio equity cannot be verified safely."""


def _positive_decimal(value: object, name: str) -> Decimal:
    if isinstance(value, bool) or value is None:
        raise PortfolioEquityUnavailable(f"{name}_unavailable")

    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise PortfolioEquityUnavailable(
            f"{name}_invalid"
        ) from None

    if not number.is_finite() or number <= 0:
        raise PortfolioEquityUnavailable(
            f"{name}_invalid"
        )

    return number


def _nonnegative_decimal(value: object, name: str) -> Decimal:
    if isinstance(value, bool) or value is None:
        raise PortfolioEquityUnavailable(f"{name}_unavailable")

    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise PortfolioEquityUnavailable(
            f"{name}_invalid"
        ) from None

    if not number.is_finite() or number < 0:
        raise PortfolioEquityUnavailable(
            f"{name}_invalid"
        )

    return number


def _currency(value: object) -> str:
    if not isinstance(value, str):
        raise PortfolioEquityUnavailable(
            "currency_unavailable"
        )

    code = value.strip().upper()

    if (
        len(code) != 3
        or not code.isascii()
        or not code.isalpha()
    ):
        raise PortfolioEquityUnavailable(
            "currency_invalid"
        )

    return code


def _timestamp(value: object) -> datetime:
    if not isinstance(value, datetime):
        raise PortfolioEquityUnavailable(
            "quote_timestamp_unavailable"
        )

    if value.tzinfo is None or value.utcoffset() is None:
        raise PortfolioEquityUnavailable(
            "quote_timestamp_not_timezone_aware"
        )

    return value.astimezone(timezone.utc)


def verify_portfolio_equity(
    *,
    cash: object,
    currency: str,
    positions: Sequence[Mapping[str, object]],
    quotes: Mapping[str, Mapping[str, object]],
    now: datetime,
    max_quote_age_seconds: int = 300,
) -> dict:
    """
    Independently calculate paper portfolio market equity.

    Inputs must be owner-scoped before this function is called.

    Quotes must have authenticated provenance and a genuine
    provider observation timestamp. This function validates
    those supplied fields; it does not fetch market data.

    Cross-currency conversion is intentionally unsupported.
    An unknown or different quote currency fails closed.

    No risk limits or broker permissions are granted here.
    """
    balance = _nonnegative_decimal(cash, "cash")
    denomination = _currency(currency)
    current_time = _timestamp(now)

    if (
        isinstance(max_quote_age_seconds, bool)
        or not isinstance(max_quote_age_seconds, int)
        or max_quote_age_seconds <= 0
    ):
        raise PortfolioEquityUnavailable(
            "invalid_quote_age_policy"
        )

    if not isinstance(positions, (list, tuple)):
        raise PortfolioEquityUnavailable(
            "positions_unavailable"
        )

    if not isinstance(quotes, Mapping):
        raise PortfolioEquityUnavailable(
            "quotes_unavailable"
        )

    total_value = Decimal("0")
    count = 0
    seen = set()
    marks = []

    for position in positions:
        if not isinstance(position, Mapping):
            raise PortfolioEquityUnavailable(
                "position_invalid"
            )

        symbol = position.get("symbol")

        if not isinstance(symbol, str) or not symbol.strip():
            raise PortfolioEquityUnavailable(
                "position_symbol_invalid"
            )

        symbol = symbol.strip().upper()

        if symbol in seen:
            raise PortfolioEquityUnavailable(
                "duplicate_position_symbol"
            )

        seen.add(symbol)

        quantity = _nonnegative_decimal(
            position.get("shares_quantity"),
            "position_quantity",
        )

        if quantity == 0:
            continue

        quote = quotes.get(symbol)

        if not isinstance(quote, Mapping):
            raise PortfolioEquityUnavailable(
                "position_quote_unavailable"
            )

        if quote.get("status") != "ok":
            raise PortfolioEquityUnavailable(
                "position_quote_not_ok"
            )

        quoted_symbol = quote.get("symbol")

        if (
            not isinstance(quoted_symbol, str)
            or quoted_symbol.strip().upper() != symbol
        ):
            raise PortfolioEquityUnavailable(
                "quote_symbol_mismatch"
            )

        if _currency(quote.get("currency")) != denomination:
            raise PortfolioEquityUnavailable(
                "currency_conversion_unavailable"
            )

        observed = _timestamp(quote.get("observed_at"))
        age = current_time - observed

        if (
            age < timedelta(0)
            or age > timedelta(seconds=max_quote_age_seconds)
        ):
            raise PortfolioEquityUnavailable(
                "quote_outside_freshness_policy"
            )

        provider = quote.get("provider")
        if not isinstance(provider, str) or not provider.strip():
            raise PortfolioEquityUnavailable(
                "quote_provider_unavailable"
            )

        price = _positive_decimal(
            quote.get("price"),
            "position_price",
        )

        position_value = quantity * price
        total_value += position_value
        count += 1

        marks.append({
            "symbol": symbol,
            "shares_quantity": str(quantity),
            "price": str(price),
            "market_value": str(position_value),
            "currency": denomination,
            "provider": provider.strip(),
            "observed_at": observed.isoformat(),
        })

    return {
        "status": "verified",
        "currency": denomination,
        "cash": str(balance),
        "gross_long_exposure": str(total_value),
        "position_market_value": str(total_value),
        "net_liquidation_value": str(
            balance + total_value
        ),
        "marked_position_count": count,
        "marks": marks,
        "risk_limits_enforced": False,
        "live_execution_allowed": False,
    }
