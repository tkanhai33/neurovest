"""DOMAIN_LOGIC_V1 market data feed facade."""

from stacks.market_data.price import get_latest_price
from stacks.market_data.bars import get_bars


def get_feed_snapshot(symbols: list[str] | None = None) -> dict:
    symbols = symbols or ["RY.TO", "TD.TO", "VFV.TO"]
    return {
        "prices": [get_latest_price(s) for s in symbols],
        "bars": {s: get_bars(s, limit=5) for s in symbols},
        "status": "ok",
    }
