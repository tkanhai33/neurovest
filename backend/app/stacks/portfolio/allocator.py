"""DOMAIN_LOGIC_V1 portfolio allocation."""

from backend.app.stacks.market_data.bars import get_bars

def allocate_cash(signal: dict, cash: float = 1000.0) -> dict:
    side = signal.get("side", "HOLD")
    if side == "BUY":
        # Get the last 5 bars for the symbol
        symbol = signal.get("symbol")
        bars = get_bars(symbol, limit=5)
        
        # Extract closing prices from the bars
        closing_prices = [bar['close'] for bar in bars]
        
        # Calculate price range variance (Max Price minus Min Price)
        if closing_prices:
            price_range_variance = max(closing_prices) - min(closing_prices)
        else:
            price_range_variance = 0
        
        # Scale the position size inversely proportional to the price range variance
        allocation = cash * 0.25 / (price_range_variance + 1)  # Adding a small constant to avoid division by zero
        allocation = min(allocation, cash * 0.15)  # Enforce hard allocation limit of 15% of total_capital
        
    elif side == "SELL":
        allocation = 0.0
    else:
        allocation = cash * 0.05
    
    return {"side": side, "cash_allocated": allocation}
