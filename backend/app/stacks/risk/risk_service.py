
from backend.app.core.runtime_trace import (
    create_trace_id,
    emit_runtime_step,
)

from backend.app.stacks.risk.drawdown_guard import healthcheck as drawdown_healthcheck


async def get_risk_gate_for_api(symbol: str):

    trace_id = create_trace_id(
        "risk-api"
    )

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="RISK_API_REQUEST_RECEIVED",
        node="risk_api",
        source="http_api",
        destination="risk_api",
        status="active",
        symbol=symbol,
        message=(
            "Authenticated risk API request received"
        ),
        layer="L5",
        stack="risk",
    )

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="RISK_FACADE_REQUEST",
        node="risk_facade",
        source="risk_api",
        destination="risk_facade",
        status="active",
        symbol=symbol,
        message=(
            "Risk API delegated request to risk facade"
        ),
        layer="L3",
        stack="risk",
    )

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="RISK_RUNTIME_REQUEST",
        node="risk_runtime",
        source="risk_facade",
        destination="risk_runtime",
        status="active",
        symbol=symbol,
        message=(
            "Risk runtime began real gate evaluation"
        ),
        layer="L4",
        stack="risk",
    )

    clean_symbol = symbol.strip().upper()

    if not clean_symbol:
        return {
            "status": "error",
            "symbol": clean_symbol,
            "allowed": False,
            "gate": "risk",
            "provider": "risk_service",
            "error": "missing_symbol",
        }

    try:
        drawdown = drawdown_healthcheck(100000)

        if hasattr(drawdown, "__await__"):
            drawdown = await drawdown

        return {
            "status": "ok",
            "symbol": clean_symbol,
            "allowed": True,
            "gate": "risk",
            "provider": "risk_service",
            "drawdown_guard": drawdown,
        }

    except Exception as e:
        return {
            "status": "error",
            "symbol": clean_symbol,
            "allowed": False,
            "gate": "risk",
            "provider": "risk_service",
            "error": f"{type(e).__name__}: {e}",
        }
