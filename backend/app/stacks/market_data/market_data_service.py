
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
