"""DOMAIN_LOGIC_V1 deterministic market bars."""

from stacks.market_data.price import normalize_symbol


def get_bars(symbol: str, limit: int = 20) -> list[dict]:
    symbol = normalize_symbol(symbol)
    limit = max(1, min(int(limit), 250))
    return [
        {
            "symbol": symbol,
            "index": i,
            "open": 100.0 + i,
            "high": 101.0 + i,
            "low": 99.0 + i,
            "close": 100.5 + i,
            "volume": 1000 + i,
        }
        for i in range(limit)
    ]
