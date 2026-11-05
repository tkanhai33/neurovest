from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Awaitable, Callable, Mapping

from backend.app.stacks.portfolio.accounting import (
    calculate_live_portfolio_equity,
)
from backend.app.stacks.journal_ledger.ledger import (
    read_portfolio_positions,
)
from backend.app.stacks.risk.portfolio_equity import (
    PortfolioEquityUnavailable,
    verify_portfolio_equity,
)


QuoteLoader = Callable[
    [str],
    Awaitable[Mapping[str, object]],
]


async def read_verified_owner_equity(
    *,
    user_id: str,
    cash_currency: str,
    quote_loader: QuoteLoader,
    now: datetime | None = None,
    max_quote_age_seconds: int = 300,
) -> dict:
    """
    Isolated paper-equity valuation adapter.

    Not an execution authorization or transaction-consistent
    risk decision. Do not use as the final order commit gate.

    The caller must supply an independently verified account
    currency and quote provider. A quote's observed_at must
    represent a genuine provider market observation, not
    merely the time the network response was received.
    """
    if not isinstance(user_id, str) or not user_id.strip():
        raise PortfolioEquityUnavailable("owner_unavailable")

    if not isinstance(cash_currency, str) or not cash_currency.strip():
        raise PortfolioEquityUnavailable("cash_currency_unavailable")

    if not callable(quote_loader):
        raise PortfolioEquityUnavailable("quote_loader_unavailable")

    owner = user_id.strip()

    # Both reads are owner-scoped. They do not form an atomic
    # snapshot; atomic enforcement belongs inside the ledger.
    try:
        cash_record = await calculate_live_portfolio_equity(
            user_id=owner,
        )
        positions = await read_portfolio_positions(
            user_id=owner,
        )
    except Exception as exc:
        raise PortfolioEquityUnavailable(
            "owner_ledger_unavailable"
        ) from exc

    if not isinstance(cash_record, Mapping):
        raise PortfolioEquityUnavailable("cash_record_invalid")

    if not isinstance(positions, (list, tuple)):
        raise PortfolioEquityUnavailable("positions_invalid")

    symbols = set()

    for position in positions:
        if not isinstance(position, Mapping):
            raise PortfolioEquityUnavailable("position_invalid")

        symbol = position.get("symbol")
        if not isinstance(symbol, str) or not symbol.strip():
            raise PortfolioEquityUnavailable("position_symbol_invalid")

        normalized = symbol.strip().upper()
        if normalized in symbols:
            raise PortfolioEquityUnavailable("duplicate_position_symbol")

        symbols.add(normalized)

    quotes = {}

    for symbol in sorted(symbols):
        try:
            quote = await quote_loader(symbol)
        except Exception as exc:
            raise PortfolioEquityUnavailable(
                "quote_provider_unavailable"
            ) from exc

        if not isinstance(quote, Mapping):
            raise PortfolioEquityUnavailable(
                "position_quote_unavailable"
            )

        quotes[symbol] = quote

    current_time = now if now is not None else datetime.now(timezone.utc)

    result = verify_portfolio_equity(
        cash=cash_record.get("current_cash_balance"),
        currency=cash_currency,
        positions=positions,
        quotes=quotes,
        now=current_time,
        max_quote_age_seconds=max_quote_age_seconds,
    )

    return {
        **result,
        "valuation_scope": "owner_scoped_non_atomic",
        "execution_approval": False,
    }
