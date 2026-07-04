"""DOMAIN_LOGIC_V1 strategy engine."""

from stacks.market_data.price import get_latest_price
from stacks.market_data.bars import get_bars
from stacks.strategy.signal import generate_signal


def generate_strategy_decision(symbol: str) -> dict:
    price = get_latest_price(symbol)
    bars = get_bars(symbol, limit=5)
    signal = generate_signal(symbol, price, bars)
    return {"symbol": symbol, "signal": signal, "status": "ok"}
