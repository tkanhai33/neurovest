"""DOMAIN_LOGIC_V1 fallback for risk."""

high_water_mark = 0.0

def healthcheck(current_balance: float) -> dict:
    global high_water_mark
    
    if current_balance > high_water_mark:
        high_water_mark = current_balance
    
    drawdown = (high_water_mark - current_balance) / high_water_mark
    if drawdown > 0.05:
        return {"status": "unhealthy", "reason": "Max trailing drawdown limit breached"}
    
    return {"status": "ok"}
