"""DOMAIN_LOGIC_V1 fallback for market_data."""

from stacks.market_data.price import get_latest_price
from stacks.market_data.bars import get_bars

class MarketDataService:
    def __init__(self):
        self.latest_prices = {}
        self.bars = {}

    def update_market_data(self, symbol: str):
        self.latest_prices[symbol] = get_latest_price(symbol)
        self.bars[symbol] = get_bars(symbol)

    def get_latest_price(self, symbol: str) -> dict:
        return self.latest_prices.get(symbol, {"symbol": symbol, "price": 0.0, "currency": "CAD", "source": "deterministic_stub"})

    def get_bars(self, symbol: str, limit: int = 20) -> list[dict]:
        return self.bars.get(symbol, [])

market_data_service = MarketDataService()
