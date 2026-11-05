"""Transaction-local market quote snapshot.

Does not fetch on its own, fabricate data, or authorize orders.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Awaitable, Callable


class TransactionQuoteUnavailable(ValueError):
    pass


def make_transaction_quote_loader(
    source_loader: Callable[[str], Awaitable[Mapping[str, Any]]],
):
    if not callable(source_loader):
        raise TransactionQuoteUnavailable("quote_loader_unavailable")

    cache: dict[str, dict] = {}

    async def load(symbol: str) -> dict:
        if (
            not isinstance(symbol, str)
            or not symbol.strip()
            or not symbol.strip().isascii()
        ):
            raise TransactionQuoteUnavailable("quote_symbol_invalid")

        name = symbol.strip().upper()

        if name not in cache:
            payload = await source_loader(name)
            if not isinstance(payload, Mapping):
                raise TransactionQuoteUnavailable("quote_unavailable")

            # Preserve genuine source fields; validators enforce
            # symbol, price, currency and observation freshness.
            cache[name] = dict(payload)

        # Do not expose the mutable cached dictionary.
        return dict(cache[name])

    return load
