"""DOMAIN_LOGIC_V1 strategy signal generation."""

def generate_signal(symbol: str, latest_price: dict, bars: list[dict]) -> dict:
    closes = [float(b["close"]) for b in bars]
    avg = sum(closes) / len(closes) if closes else float(latest_price["price"])
    price = float(latest_price["price"])

    if price > avg:
        side = "BUY"
    elif price < avg:
        side = "SELL"
    else:
        side = "HOLD"

    return {
        "symbol": symbol,
        "side": side,
        "price": price,
        "average_close": avg
    }
