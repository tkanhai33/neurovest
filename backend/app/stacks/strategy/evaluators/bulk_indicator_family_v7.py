"""Seventh qualified batch: deterministic daily single-symbol OHLCV strategies."""

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

SEVENTH_FIFTEEN_OHLCV_NAMES = (
    "200-Day Moving Average Tactical Allocation",
    "Drawdown Circuit Breaker",
    "High Tight Flag",
    "Historical Volatility Regime",
    "Pivot Point Breakout",
    "Pivot Point Reversion",
    "Price Channel Mean Reversion",
    "Previous Day High Low Breakout",
    "Previous Day High Low Fade",
    "Realized Volatility Mean Reversion",
    "Trend Breakout Ensemble",
    "Trend Regime Switching",
    "Trend Strength Weighted Position",
    "Trend Template",
    "Volatility Circuit Breaker",
)


def _returns(closes: Sequence[float], period: int) -> float:
    return closes[-1] / closes[-1 - period] - 1.0


def _evaluate(name: str, bars: Sequence[object]) -> Result:
    try:
        closes = _series(bars, "close")
        highs = _series(bars, "high")
        lows = _series(bars, "low")
        _series(bars, "volume")
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
    daily_returns = [
        closes[index] / closes[index - 1] - 1.0
        for index in range(1, len(closes))
    ]

    if name == "200-Day Moving Average Tactical Allocation":
        if len(closes) < 200:
            return _abstain(name, "insufficient_200_day_history")
        ma200 = mean(closes[-200:])
        decision = "BUY" if close > ma200 else "SELL"
        return _result(
            name,
            decision,
            abs(close - ma200) / max(close, 1.0) * 8.0,
            "two_hundred_day_trend",
        )

    if name == "Drawdown Circuit Breaker":
        peak = max(closes[-126:])
        drawdown = close / peak - 1.0
        decision = "SELL" if drawdown <= -0.10 else "HOLD"
        return _result(
            name,
            decision,
            abs(drawdown) * 8.0,
            "one_hundred_twenty_six_day_drawdown",
        )

    if name == "High Tight Flag":
        run_up = _returns(closes, 40)
        consolidation = (
            max(highs[-15:]) - min(lows[-15:])
        ) / max(mean(closes[-15:]), 1.0)
        decision = "BUY" if run_up >= 0.15 and consolidation <= 0.10 else "HOLD"
        return _result(
            name,
            decision,
            max(run_up - consolidation, 0.0) * 4.0,
            "high_tight_flag",
        )

    if name == "Historical Volatility Regime":
        volatility = pstdev(daily_returns[-20:])
        long_volatility = pstdev(daily_returns[-60:])
        decision = "BUY" if volatility <= long_volatility else "HOLD"
        return _result(
            name,
            decision,
            abs(volatility - long_volatility) * 25.0,
            "historical_volatility_regime",
        )

    if name in {"Pivot Point Breakout", "Pivot Point Reversion"}:
        pivot = (highs[-2] + lows[-2] + closes[-2]) / 3.0
        range_value = max(highs[-2] - lows[-2], 1e-9)
        resistance = 2.0 * pivot - lows[-2]
        support = 2.0 * pivot - highs[-2]

        if name == "Pivot Point Breakout":
            decision = (
                "BUY" if close > resistance
                else "SELL" if close < support
                else "HOLD"
            )
            boundary = resistance if decision == "BUY" else support
            reason = "previous_day_pivot_breakout"
        else:
            decision = (
                "SELL" if close >= resistance * 0.995
                else "BUY" if close <= support * 1.005
                else "HOLD"
            )
            boundary = resistance if decision == "SELL" else support
            reason = "previous_day_pivot_reversion"

        return _result(
            name,
            decision,
            abs(close - boundary) / range_value,
            reason,
        )

    if name == "Price Channel Mean Reversion":
        upper = max(highs[-20:])
        lower = min(lows[-20:])
        midpoint = (upper + lower) / 2.0
        decision = "BUY" if close < midpoint else "SELL"
        return _result(
            name,
            decision,
            abs(close - midpoint) / max(upper - lower, 1e-9),
            "price_channel_mean_reversion",
        )

    if name in {
        "Previous Day High Low Breakout",
        "Previous Day High Low Fade",
    }:
        previous_high = highs[-2]
        previous_low = lows[-2]

        if name == "Previous Day High Low Breakout":
            decision = (
                "BUY" if close > previous_high
                else "SELL" if close < previous_low
                else "HOLD"
            )
            boundary = previous_high if decision == "BUY" else previous_low
            reason = "previous_day_range_breakout"
        else:
            decision = (
                "SELL" if close >= previous_high * 0.997
                else "BUY" if close <= previous_low * 1.003
                else "HOLD"
            )
            boundary = previous_high if decision == "SELL" else previous_low
            reason = "previous_day_range_fade"

        return _result(
            name,
            decision,
            abs(close - boundary) / max(close, 1.0) * 15.0,
            reason,
        )

    if name == "Realized Volatility Mean Reversion":
        current_volatility = pstdev(daily_returns[-20:])
        long_volatility = pstdev(daily_returns[-60:])
        decision = "BUY" if current_volatility > long_volatility else "HOLD"
        return _result(
            name,
            decision,
            abs(current_volatility - long_volatility) * 30.0,
            "realized_volatility_mean_reversion",
        )

    if name == "Trend Breakout Ensemble":
        fast_breakout = close > max(highs[-21:-1])
        slow_breakout = close > max(highs[-56:-1])
        decision = "BUY" if fast_breakout and slow_breakout else "HOLD"
        return _result(
            name,
            decision,
            abs(_returns(closes, 20)) * 6.0,
            "multi_horizon_trend_breakout",
        )

    if name == "Trend Regime Switching":
        fast = _ema(closes[-25:], 10)
        slow = _ema(closes[-60:], 30)
        volatility = pstdev(daily_returns[-20:])
        long_volatility = pstdev(daily_returns[-60:])
        decision = (
            "BUY" if fast > slow and volatility <= long_volatility * 1.5
            else "SELL" if fast < slow
            else "HOLD"
        )
        return _result(
            name,
            decision,
            abs(fast - slow) / max(abs(slow), 1.0) * 100.0,
            "trend_volatility_regime",
        )

    if name == "Trend Strength Weighted Position":
        directional_move = abs(_returns(closes, 20))
        noise = max(pstdev(daily_returns[-20:]), 1e-9)
        strength = directional_move / noise
        decision = "BUY" if closes[-1] > ma50 else "SELL"
        return _result(
            name,
            decision,
            strength / 10.0,
            "volatility_adjusted_trend_strength",
        )

    if name == "Trend Template":
        if len(closes) < 200:
            return _abstain(name, "insufficient_trend_template_history")
        ma200 = mean(closes[-200:])
        high_52 = max(highs[-252:]) if len(highs) >= 252 else max(highs)
        decision = (
            "BUY" if close > ma20 > ma50 > ma200
            and close >= high_52 * 0.75
            else "HOLD"
        )
        return _result(
            name,
            decision,
            abs(close - ma200) / max(close, 1.0) * 6.0,
            "multi_moving_average_trend_template",
        )

    if name == "Volatility Circuit Breaker":
        current_volatility = pstdev(daily_returns[-20:])
        long_volatility = max(pstdev(daily_returns[-60:]), 1e-9)
        ratio = current_volatility / long_volatility
        decision = "SELL" if ratio >= 2.0 else "HOLD"
        return _result(
            name,
            decision,
            abs(ratio - 1.0),
            "volatility_circuit_breaker",
        )

    return _abstain(name, "unsupported_v7_strategy")


def _make_evaluator(name: str) -> Callable[[Sequence[object]], Result]:
    def evaluator(bars: Sequence[object]) -> Result:
        return _evaluate(name, bars)

    evaluator.__name__ = "evaluate_" + (
        name.lower()
        .replace("-", "_")
        .replace(" ", "_")
    )
    return evaluator


BULK_OFFLINE_EVALUATORS_V7 = {
    name: _make_evaluator(name)
    for name in SEVENTH_FIFTEEN_OHLCV_NAMES
}


def healthcheck() -> dict[str, object]:
    return {
        "status": "ok",
        "strategy_count": 15,
        "offline_only": True,
        "registry_activated": False,
        "execution_enabled": False,
    }
