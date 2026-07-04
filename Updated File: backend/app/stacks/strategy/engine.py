"""DOMAIN_LOGIC_V1 strategy engine."""

from app.stacks.market_data.price import get_latest_price
from app.stacks.market_data.bars import get_bars
from app.stacks.strategy.signal import generate_signal
from app.stacks.risk.drawdown_guard import check_risk_limits

def generate_strategy_decision(symbol: str) -> dict:
    price = get_latest_price(symbol)
    bars = get_bars(symbol, limit=5)
    signal = generate_signal(symbol, price, bars)

    # Perform risk check
    risk_check_result = check_risk_limits(signal)
    if not risk_check_result["approved"]:
        return {
            "symbol": symbol,
            "signal": signal,
            "status": "blocked_by_risk",
            "reason": risk_check_result["reason"]
        }

    return {"symbol": symbol, "signal": signal, "status": "ok"}
