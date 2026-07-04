"""DOMAIN_LOGIC_V1 strategy engine."""

from stacks.market_data.price import get_latest_price
from stacks.market_data.bars import get_bars
from stacks.strategy.signal import generate_signal

class StrategyEngine:
    def __init__(self, market_data_service: MarketDataService):
        self.market_data_service = market_data_service

    def generate_strategy_decision(self, symbol: str) -> dict:
        price = self.market_data_service.get_latest_price(symbol)
        bars = self.market_data_service.get_bars(symbol, limit=5)
        signal = generate_signal(symbol, price, bars)
        return {"symbol": symbol, "signal": signal, "status": "ok"}

strategy_engine = StrategyEngine(market_data_service)
