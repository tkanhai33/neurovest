"""DOMAIN_LOGIC_V1 system portfolio rebalancing and trade execution engine."""

def rebalance_portfolio(signal: dict) -> dict:
    """Processes incoming system signal vectors and prepares rebalancing parameters."""
    if isinstance(signal, dict) and signal.get('status') == 'ok':
        action = signal.get('signal', {}).get('action') if isinstance(signal.get('signal'), dict) else signal.get('action', 'hold')
        return {
            "symbol": signal.get("symbol", "UNKNOWN"),
            "signal": action,
            "status": "rebalanced"
        }
    return {"status": "no_action"}

def execute_trade(symbol: str, signal: str) -> dict:
    """Simulates market transaction fills and outputs a fully structured trade execution token."""
    # Handle both dictionary objects or raw strings safely for our fallback loops
    action_str = signal.get("action", "hold") if isinstance(signal, dict) else str(signal)

    return {
        "symbol": symbol,
        "signal": action_str,
        "status": "executed"
    }
