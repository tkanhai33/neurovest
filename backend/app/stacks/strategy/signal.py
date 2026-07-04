"""DOMAIN_LOGIC_V1 strategy signal generation."""

import numpy as np

def generate_signal(symbol: str, latest_price: dict, bars: list[dict], lookback_period: int = 14) -> dict:
    # Extract closing prices from the bars input stream parameter
    closing_prices = [bar['close'] for bar in bars]
    
    # Calculate price differences over the lookback period
    price_differences = np.diff(closing_prices)
    
    if len(price_differences) < lookback_period:
        return {"status": "no_action", "action": "hold", "symbol": symbol}
    
    gains = price_differences[price_differences > 0]
    losses = -price_differences[price_differences < 0]
    
    # Calculate average gain and loss
    avg_gain = np.mean(gains)
    avg_loss = np.mean(losses)
    
    # Calculate the relative strength (RS) ratio
    rs = avg_gain / avg_loss
    
    # Translate RS into a standard 0-to-100 RSI indicator bound framework
    rsi = 100 - (100 / (1 + rs))
    
    # Set rule thresholds
    if rsi < 30:
        return {"status": "ok", "action": "buy", "symbol": symbol}
    elif rsi > 70:
        return {"status": "ok", "action": "sell", "symbol": symbol}
    else:
        return {"status": "no_action", "action": "hold", "symbol": symbol}
