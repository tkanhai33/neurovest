
from backend.app.core.runtime_trace import (
    create_trace_id,
    emit_runtime_step,
)

from backend.app.stacks.strategy.engine import generate_strategy_decision


async def get_strategy_decision_for_api(symbol: str):

    trace_id = create_trace_id(
        "strategy-api"
    )

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="STRATEGY_API_REQUEST_RECEIVED",
        node="strategy_api",
        source="http_api",
        destination="strategy_api",
        status="active",
        symbol=symbol,
        message=(
            "Authenticated strategy API request received"
        ),
        layer="L5",
        stack="strategy",
    )

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="STRATEGY_FACADE_REQUEST",
        node="strategy_facade",
        source="strategy_api",
        destination="strategy_facade",
        status="active",
        symbol=symbol,
        message=(
            "Strategy API delegated request to strategy facade"
        ),
        layer="L3",
        stack="strategy",
    )

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="STRATEGY_RUNTIME_REQUEST",
        node="strategy_runtime",
        source="strategy_facade",
        destination="strategy_runtime",
        status="active",
        symbol=symbol,
        message=(
            "Strategy runtime began real decision processing"
        ),
        layer="L4",
        stack="strategy",
    )

    clean_symbol = symbol.strip().upper()

    if not clean_symbol:
        return {
            "status": "error",
            "symbol": clean_symbol,
            "decision": "hold",
            "confidence": 0,
            "provider": "strategy_service",
            "error": "missing_symbol",
        }

    try:
        result = generate_strategy_decision(clean_symbol)

        if hasattr(result, "__await__"):
            result = await result

        if isinstance(result, dict):
            result.setdefault("status", "ok")
            result.setdefault("symbol", clean_symbol)
            result.setdefault("provider", "strategy_engine")
            return result

        return {
            "status": "ok",
            "symbol": clean_symbol,
            "decision": str(result),
            "confidence": 0,
            "provider": "strategy_engine",
        }

    except Exception as e:
        return {
            "status": "error",
            "symbol": clean_symbol,
            "decision": "hold",
            "confidence": 0,
            "provider": "strategy_service",
            "error": f"{type(e).__name__}: {e}",
        }
