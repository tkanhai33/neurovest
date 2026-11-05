"""Sixth qualified batch: deterministic single-symbol OHLCV strategies."""

from __future__ import annotations

from collections.abc import Sequence
from statistics import mean, pstdev
from typing import Callable

from backend.app.stacks.strategy.evaluators.bulk_indicator_family_v5 import (
    _abstain,
    _atr,
    _ema,
    _result,
    _series,
)

Result = dict[str, object]

SIXTH_FIFTEEN_OHLCV_NAMES = (
    "ATR Trailing Stop Trend",
    "Autocorrelation Momentum",
    "Autocorrelation Reversal",
    "Close Location Value Momentum",
    "Close Location Value Reversal",
    "Failed Breakout Reversal",
    "False Breakdown Reversal",
    "Half-Life Mean Reversion",
    "Keltner Bollinger Squeeze",
    "Mean Reversion with Trend Filter",
    "Momentum Ensemble",
    "RSI Divergence Reversal",
    "RSI Pullback in Uptrend",
    "Volatility Compression Breakout",
    "Volatility Momentum",
)


def _rsi(closes: Sequence[float], period: int = 14) -> float:
    changes = [
        closes[index] - closes[index - 1]
        for index in range(1, len(closes))
    ]
    gains = [max(change, 0.0) for change in changes[-period:]]
    losses = [max(-change, 0.0) for change in changes[-period:]]
    average_gain = mean(gains)
    average_loss = mean(losses)
    if average_loss == 0.0:
        return 100.0
    return 100.0 - 100.0 / (1.0 + average_gain / average_loss)


def _returns(closes: Sequence[float], lookback: int) -> float:
    return closes[-1] / closes[-1 - lookback] - 1.0


def _evaluate(name: str, bars: Sequence[object]) -> Result:
    try:
        closes = _series(bars, "close")
        highs = _series(bars, "high")
        lows = _series(bars, "low")
        volumes = _series(bars, "volume")
    except (AttributeError, KeyError, TypeError, ValueError):
        return _abstain(name, "invalid_ohlcv_bars")

    if len(closes) < 80:
        return _abstain(name, "insufficient_ohlcv_history")

    close = closes[-1]
    if close <= 0.0:
        return _abstain(name, "invalid_close")

    ma20 = mean(closes[-20:])
    ma50 = mean(closes[-50:])
    atr20 = _atr(highs, lows, closes)
    rsi14 = _rsi(closes[-30:])
    daily_returns = [
        closes[index] / closes[index - 1] - 1.0
        for index in range(1, len(closes))
    ]

    if name == "ATR Trailing Stop Trend":
        stop = max(highs[-23:-1]) - 3.0 * atr20
        return _result(
            name,
            "BUY" if close > stop else "SELL",
            abs(close - stop) / close * 10.0,
            "atr_trailing_stop",
        )

    if name in {"Autocorrelation Momentum", "Autocorrelation Reversal"}:
        recent = daily_returns[-40:]
        center = mean(recent)
        numerator = sum(
            (recent[index] - center) * (recent[index - 1] - center)
            for index in range(1, len(recent))
        )
        denominator = sum((value - center) ** 2 for value in recent)
        correlation = numerator / denominator if denominator else 0.0
        trend = _returns(closes, 20)
        if name == "Autocorrelation Momentum":
            decision = "BUY" if correlation * trend >= 0 else "SELL"
        else:
            decision = "SELL" if correlation * trend >= 0 else "BUY"
        return _result(name, decision, abs(correlation) * abs(trend) * 25.0, "return_autocorrelation")

    if name in {
        "Close Location Value Momentum",
        "Close Location Value Reversal",
    }:
        clv = [
            (2.0 * closes[index] - highs[index] - lows[index])
            / max(highs[index] - lows[index], 1e-9)
            for index in range(-10, 0)
        ]
        score = mean(clv)
        momentum = score > 0.0
        if name == "Close Location Value Momentum":
            decision = "BUY" if momentum else "SELL"
        else:
            decision = "SELL" if momentum else "BUY"
        return _result(name, decision, abs(score), "close_location_value")

    if name == "Failed Breakout Reversal":
        prior_high = max(highs[-21:-2])
        decision = "SELL" if highs[-2] > prior_high and close < prior_high else "HOLD"
        return _result(name, decision, abs(close - prior_high) / close * 15.0, "failed_high_breakout")

    if name == "False Breakdown Reversal":
        prior_low = min(lows[-21:-2])
        decision = "BUY" if lows[-2] < prior_low and close > prior_low else "HOLD"
        return _result(name, decision, abs(close - prior_low) / close * 15.0, "false_low_breakdown")

    if name == "Half-Life Mean Reversion":
        deviations = [value - ma20 for value in closes[-20:]]
        numerator = sum(
            deviations[index - 1] * deviations[index]
            for index in range(1, len(deviations))
        )
        denominator = sum(value * value for value in deviations[:-1])
        phi = numerator / denominator if denominator else 0.0
        decision = "BUY" if close < ma20 else "SELL"
        return _result(name, decision, min(abs(1.0 - phi), 1.0), "mean_reversion_half_life")

    if name == "Keltner Bollinger Squeeze":
        width = (max(closes[-20:]) - min(closes[-20:])) / ma20
        keltner_width = 4.0 * atr20 / ma20
        if width < keltner_width:
            decision = "BUY" if close > ma20 else "SELL"
        else:
            decision = "HOLD"
        return _result(name, decision, abs(keltner_width - width) * 10.0, "keltner_bollinger_squeeze")

    if name == "Mean Reversion with Trend Filter":
        decision = (
            "BUY" if close < ma20 and ma20 > ma50
            else "SELL" if close > ma20 and ma20 < ma50
            else "HOLD"
        )
        return _result(name, decision, abs(close - ma20) / close * 15.0, "trend_filtered_mean_reversion")

    if name == "Momentum Ensemble":
        score = mean([
            _returns(closes, 20),
            _returns(closes, 60),
            _returns(closes, 79),
        ])
        return _result(name, "BUY" if score > 0 else "SELL", abs(score) * 8.0, "multi_horizon_momentum")

    if name == "RSI Divergence Reversal":
        prior_rsi = _rsi(closes[-45:-15])
        prior_close = closes[-16]
        decision = (
            "BUY" if close < prior_close and rsi14 > prior_rsi
            else "SELL" if close > prior_close and rsi14 < prior_rsi
            else "HOLD"
        )
        return _result(name, decision, abs(rsi14 - prior_rsi) / 100.0, "rsi_price_divergence")

    if name == "RSI Pullback in Uptrend":
        decision = "BUY" if ma20 > ma50 and 35.0 <= rsi14 <= 55.0 else "HOLD"
        return _result(name, decision, abs(50.0 - rsi14) / 50.0, "rsi_uptrend_pullback")

    if name == "Volatility Compression Breakout":
        current_volatility = pstdev(daily_returns[-20:])
        prior_volatility = pstdev(daily_returns[-40:-20])
        decision = (
            "BUY" if current_volatility < prior_volatility and close > max(highs[-6:-1])
            else "SELL" if current_volatility < prior_volatility and close < min(lows[-6:-1])
            else "HOLD"
        )
        return _result(name, decision, abs(prior_volatility - current_volatility) * 20.0, "volatility_compression_breakout")

    if name == "Volatility Momentum":
        momentum = _returns(closes, 20)
        volatility = max(pstdev(daily_returns[-20:]), 1e-9)
        score = momentum / volatility
        return _result(name, "BUY" if score > 0 else "SELL", abs(score) / 10.0, "volatility_scaled_momentum")

    return _abstain(name, "unsupported_v6_strategy")


def _make_evaluator(name: str) -> Callable[[Sequence[object]], Result]:
    def evaluator(bars: Sequence[object]) -> Result:
        return _evaluate(name, bars)

    evaluator.__name__ = "evaluate_" + (
        name.lower().replace("-", "_").replace(" ", "_")
    )
    return evaluator


BULK_OFFLINE_EVALUATORS_V6 = {
    name: _make_evaluator(name)
    for name in SIXTH_FIFTEEN_OHLCV_NAMES
}


def healthcheck() -> dict[str, object]:
    return {
        "status": "ok",
        "strategy_count": 15,
        "offline_only": True,
        "registry_activated": False,
        "execution_enabled": False,
    }
