"""DOMAIN_LOGIC_V1 strategy signal generation."""

def generate_signal(symbol: str, latest_price: dict, bars: list[dict]) -> dict:
    # Forces an explicit buy condition to test our database pipeline architecture
    return {
        "status": "ok",
        "action": "buy",
        "symbol": symbol
    }
