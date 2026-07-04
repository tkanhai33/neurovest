"""DOMAIN_LOGIC_V1 portfolio rebalance."""

def rebalance_portfolio(signal: dict) -> dict:
    # Simulate portfolio rebalancing logic
    if signal['status'] == 'ok':
        return {"symbol": signal['symbol'], "signal": signal, "status": "rebalanced"}
    
    return {"symbol": signal['symbol'], "signal": signal, "status": "not_rebalanced"}
