from pydantic import BaseModel

class MarketDataService:
    def __init__(self):
        self.latest_prices = {}
        self.bars = {}

    async def update_market_data(self, symbol: str):
        self.latest_prices[symbol] = {"symbol": symbol, "price": 100.0 + len(symbol), "currency": "CAD", "source": "deterministic_stub"}
        self.bars[symbol] = [{"index": i, "open": 100.0 + i, "high": 101.0 + i, "low": 99.0 + i, "close": 100.5 + i, "volume": 1000 + i} for i in range(20)]

    async def get_latest_price(self, symbol: str) -> dict:
        return self.latest_prices.get(symbol, {"symbol": symbol, "price": 0.0, "currency": "CAD", "source": "deterministic_stub"})

    async def get_bars(self, symbol: str, limit: int = 20) -> list[dict]:
        return self.bars.get(symbol, [])
