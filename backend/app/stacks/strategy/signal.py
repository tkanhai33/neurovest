"""RSI-only replay-safe strategy signal generation.

Restored after 130C showed multi-indicator v1 underperformed baseline.
"""

from __future__ import annotations

import numpy as np


def generate_signal(symbol: str, latest_price: dict, bars: list[dict], lookback_period: int = 14) -> dict:
    closing_prices = [float(bar["close"]) for bar in bars if "close" in bar]

    if len(closing_prices) < lookback_period + 1:
        return {"status": "no_action", "action": "hold", "decision": "HOLD", "symbol": symbol}

    window = closing_prices[-(lookback_period + 1):]
    diffs = np.diff(window)

    gains = np.where(diffs > 0, diffs, 0.0)
    losses = np.where(diffs < 0, -diffs, 0.0)

    avg_gain = float(np.mean(gains))
    avg_loss = float(np.mean(losses))

    if avg_loss == 0:
        rsi = 100.0
    elif avg_gain == 0:
        rsi = 0.0
    else:
        rs = avg_gain / avg_loss
        rsi = 100.0 - (100.0 / (1.0 + rs))

    if rsi <= 45:
        action = "buy"
    elif rsi >= 55:
        action = "sell"
    else:
        action = "hold"

    return {
        "status": "ok",
        "symbol": symbol,
        "action": action,
        "decision": action.upper(),
        "rsi": round(rsi, 2),
        "confidence": round(abs(rsi - 50.0) / 50.0, 3),
    }
