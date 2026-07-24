from backend.app.stacks.strategy.engine import generate_strategy_decision


async def get_strategy_decision_for_api(symbol: str):
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
