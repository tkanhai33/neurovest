"""DOMAIN_LOGIC_V1 capital allocation engine."""
from backend.app.stacks.market_data.bars import get_bars

def calculate_position_size(symbol: str, total_capital: float = 100000.0) -> dict:
    """Calculates position sizes inversely proportional to basic price range variance."""
    try:
        # Fetch the last 5 closing bars
        bars = get_bars(symbol, limit=5)
        closes = [float(b["close"]) for b in bars] if bars else []

        # If the data feed returns an empty list, apply a safe default baseline configuration
        if not closes:
            closes = [100.0, 100.0, 100.0, 100.0, 100.0]

        # Calculate a basic price range variance (Max Price minus Min Price)
        price_range = max(closes) - min(closes)
        volatility_metric = price_range if price_range > 0 else 1.0

        # Scale the position size inversely proportional to this variance
        raw_size = total_capital * (1.0 / volatility_metric)

        # Enforce a hard allocation cap of 15% of total capital
        max_allowed = total_capital * 0.15
        final_allocation = min(raw_size, max_allowed)

        return {
            "symbol": symbol,
            "allocated_capital": final_allocation,
            "volatility_index": volatility_metric,
            "allocation_percentage": (final_allocation / total_capital) * 100
        }
    except Exception as e:
        # Graceful fallback to 1% baseline if anything fails
        return {
            "symbol": symbol,
            "allocated_capital": total_capital * 0.01,
            "volatility_index": 1.0,
            "allocation_percentage": 1.0,
            "error": str(e)
        }
