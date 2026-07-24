from backend.app.stacks.risk.drawdown_guard import healthcheck as drawdown_healthcheck


async def get_risk_gate_for_api(symbol: str):
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
