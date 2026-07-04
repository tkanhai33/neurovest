"""DOMAIN_LOGIC_V1 market price normalization."""

DEFAULT_PRICES = {
    "RY.TO": 142.50,
    "TD.TO": 82.25,
    "VFV.TO": 135.10,
}


def normalize_symbol(symbol: str) -> str:
    return symbol.strip().upper()


def get_latest_price(symbol: str) -> dict:
    symbol = normalize_symbol(symbol)
    price = DEFAULT_PRICES.get(symbol, 100.0)
    return {"symbol": symbol, "price": float(price), "currency": "CAD", "source": "deterministic_stub"}
