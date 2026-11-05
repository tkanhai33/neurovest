
import asyncio
from datetime import UTC, datetime, timedelta

from backend.app.core.runtime_trace import (
    create_trace_id,
    emit_runtime_step,
)

from backend.app.stacks.market_data.feed import get_live_price_quote


async def get_live_market_price_for_api(symbol: str):

    trace_id = create_trace_id(
        "market-api"
    )

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="MARKET_API_REQUEST_RECEIVED",
        node="market_api",
        source="http_api",
        destination="market_api",
        status="active",
        symbol=symbol,
        message=(
            "Authenticated market-data API request received"
        ),
        layer="L5",
        stack="market_data",
    )

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="MARKET_FACADE_REQUEST",
        node="market_data_facade",
        source="market_api",
        destination="market_data_facade",
        status="active",
        symbol=symbol,
        message=(
            "Market API delegated request to market-data facade"
        ),
        layer="L3",
        stack="market_data",
    )

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="MARKET_RUNTIME_REQUEST",
        node="market_runtime",
        source="market_data_facade",
        destination="market_runtime",
        status="active",
        symbol=symbol,
        message=(
            "Market-data runtime began real quote processing"
        ),
        layer="L4",
        stack="market_data",
    )

    return await get_live_price_quote(symbol)


_BULK_QUOTE_CACHE_TTL = timedelta(seconds=30)
_BULK_QUOTE_MAX_SYMBOLS = 250
_BULK_QUOTE_CONCURRENCY = 8
_bulk_quote_cache: dict[
    str,
    tuple[datetime, dict[str, object]],
] = {}


async def get_live_market_prices_for_api(
    symbols: list[str],
) -> dict[str, object]:
    normalized: list[str] = []

    for value in symbols:
        symbol = str(value or "").strip().upper()

        if symbol and symbol not in normalized:
            normalized.append(symbol)

    if not normalized:
        return {
            "status": "error",
            "quotes": {},
            "error": "missing_symbols",
        }

    if len(normalized) > _BULK_QUOTE_MAX_SYMBOLS:
        return {
            "status": "error",
            "quotes": {},
            "error": (
                "too_many_symbols:"
                f"{_BULK_QUOTE_MAX_SYMBOLS}"
            ),
        }

    now = datetime.now(UTC)
    semaphore = asyncio.Semaphore(
        _BULK_QUOTE_CONCURRENCY
    )

    async def load_one(
        symbol: str,
    ) -> tuple[str, dict[str, object]]:
        cached = _bulk_quote_cache.get(symbol)

        if (
            cached is not None
            and now - cached[0] <= _BULK_QUOTE_CACHE_TTL
        ):
            return symbol, cached[1]

        async with semaphore:
            try:
                quote = await get_live_price_quote(symbol)
            except Exception as exc:
                return symbol, {
                    "status": "error",
                    "symbol": symbol,
                    "price": None,
                    "provider": "yfinance",
                    "error": (
                        f"{type(exc).__name__}: {exc}"
                    ),
                }

        if quote.get("status") == "ok":
            _bulk_quote_cache[symbol] = (
                datetime.now(UTC),
                quote,
            )

        return symbol, quote

    loaded = await asyncio.gather(
        *(
            load_one(symbol)
            for symbol in normalized
        )
    )

    return {
        "status": "ok",
        "quotes": dict(loaded),
        "requested_count": len(normalized),
        "cache_ttl_seconds": 30,
        "provider_concurrency": _BULK_QUOTE_CONCURRENCY,
    }
