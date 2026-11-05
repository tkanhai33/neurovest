"""Eighth qualified batch: deterministic daily single-symbol OHLCV strategies."""

from __future__ import annotations

from collections.abc import Sequence
from math import log
from statistics import mean, pstdev
from typing import Callable

from backend.app.stacks.strategy.evaluators.bulk_indicator_family_v5 import (
    _abstain,
    _ema,
    _result,
    _series,
)

Result = dict[str, object]

EIGHTH_FIFTEEN_STRICT_OHLCV_NAMES = (
    "Absolute Momentum",
    "Downside Volatility",
    "Hurst Exponent Regime",
    "Low Volatility",
    "Low Volatility Momentum",
    "Mean Reversion Ensemble",
    "Multi-Horizon Momentum",
    "Multi-Horizon Trend",
    "Post-Gap Consolidation Breakout",
    "Trend with Drawdown Filter",
    "Volatility Contraction Pattern",
    "Volatility Managed Momentum",
    "Volatility Regime Switching",
    "Volatility-Scaled Momentum",
    "Volatility-Scaled Trend",
)


def _returns(closes: Sequence[float], period: int) -> float:
    return closes[-1] / closes[-1 - period] - 1.0


def _rsi(closes: Sequence[float], period: int = 14) -> float:
    changes = [
        closes[index] - closes[index - 1]
        for index in range(1, len(closes))
    ]
    gains = [max(change, 0.0) for change in changes[-period:]]
    losses = [max(-change, 0.0) for change in changes[-period:]]
    average_loss = mean(losses)

    if average_loss == 0.0:
        return 100.0

    return 100.0 - (
        100.0 / (1.0 + mean(gains) / average_loss)
    )


def _evaluate(name: str, bars: Sequence[object]) -> Result:
    try:
        closes = _series(bars, "close")
        highs = _series(bars, "high")
        lows = _series(bars, "low")
        _series(bars, "volume")
    except (AttributeError, KeyError, TypeError, ValueError):
        return _abstain(name, "invalid_ohlcv_bars")

    if len(closes) < 130:
        return _abstain(name, "insufficient_ohlcv_history")

    close = closes[-1]

    if close <= 0.0:
        return _abstain(name, "invalid_close")

    daily_returns = [
        closes[index] / closes[index - 1] - 1.0
        for index in range(1, len(closes))
    ]

    ma20 = mean(closes[-20:])
    ma50 = mean(closes[-50:])
    ma100 = mean(closes[-100:])
    current_volatility = pstdev(daily_returns[-20:])
    long_volatility = max(pstdev(daily_returns[-60:]), 1e-9)
    momentum20 = _returns(closes, 20)

    if name == "Absolute Momentum":
        momentum = _returns(closes, 126)
        return _result(
            name,
            "BUY" if momentum > 0.0 else "SELL",
            abs(momentum) * 4.0,
            "one_hundred_twenty_six_day_absolute_momentum",
        )

    if name == "Downside Volatility":
        downside = [
            value for value in daily_returns[-20:]
            if value < 0.0
        ]
        downside_volatility = pstdev(downside) if len(downside) > 1 else 0.0
        decision = (
            "BUY"
            if downside_volatility <= long_volatility
            else "HOLD"
        )
        return _result(
            name,
            decision,
            abs(long_volatility - downside_volatility) * 30.0,
            "downside_return_volatility",
        )

    if name == "Hurst Exponent Regime":
        window = closes[-100:]
        deviations = [value - mean(window) for value in window]
        cumulative = []
        total = 0.0

        for value in deviations:
            total += value
            cumulative.append(total)

        span = max(cumulative) - min(cumulative)
        deviation = max(pstdev(window), 1e-9)
        hurst = log(max(span / deviation, 1e-9)) / log(len(window))
        decision = (
            "BUY" if hurst >= 0.55
            else "SELL" if hurst <= 0.45
            else "HOLD"
        )
        return _result(
            name,
            decision,
            abs(hurst - 0.5) * 4.0,
            "rescaled_range_hurst_regime",
        )

    if name == "Low Volatility":
        decision = (
            "BUY"
            if current_volatility <= long_volatility
            else "HOLD"
        )
        return _result(
            name,
            decision,
            abs(current_volatility - long_volatility) * 25.0,
            "current_vs_long_volatility",
        )

    if name == "Low Volatility Momentum":
        decision = (
            "BUY"
            if momentum20 > 0.0
            and current_volatility <= long_volatility
            else "HOLD"
        )
        return _result(
            name,
            decision,
            abs(momentum20) / long_volatility / 10.0,
            "low_volatility_positive_momentum",
        )

    if name == "Mean Reversion Ensemble":
        rsi = _rsi(closes[-30:])
        deviation = (close - ma20) / max(ma20, 1.0)
        decision = (
            "BUY" if deviation <= -0.02 and rsi <= 40.0
            else "SELL" if deviation >= 0.02 and rsi >= 60.0
            else "HOLD"
        )
        return _result(
            name,
            decision,
            abs(deviation) * 20.0 + abs(rsi - 50.0) / 100.0,
            "moving_average_rsi_mean_reversion_ensemble",
        )

    if name == "Multi-Horizon Momentum":
        score = mean(
            [
                _returns(closes, 20),
                _returns(closes, 60),
                _returns(closes, 120),
            ]
        )
        return _result(
            name,
            "BUY" if score > 0.0 else "SELL",
            abs(score) * 6.0,
            "twenty_sixty_one_twenty_momentum",
        )

    if name == "Multi-Horizon Trend":
        fast = _ema(closes[-25:], 10)
        medium = _ema(closes[-60:], 25)
        slow = _ema(closes[-120:], 50)
        decision = (
            "BUY" if fast > medium > slow
            else "SELL" if fast < medium < slow
            else "HOLD"
        )
        return _result(
            name,
            decision,
            abs(fast - slow) / max(abs(slow), 1.0) * 100.0,
            "multi_horizon_ema_trend",
        )

    if name == "Post-Gap Consolidation Breakout":
        gap = closes[-15] / closes[-16] - 1.0
        consolidation_high = max(highs[-14:-1])
        consolidation_low = min(lows[-14:-1])
        consolidation_width = (
            consolidation_high - consolidation_low
        ) / max(consolidation_low, 1.0)
        decision = (
            "BUY"
            if gap >= 0.02
            and consolidation_width <= 0.10
            and close > consolidation_high
            else "HOLD"
        )
        return _result(
            name,
            decision,
            abs(gap) * 10.0,
            "post_gap_consolidation_breakout",
        )

    if name == "Trend with Drawdown Filter":
        peak = max(closes[-126:])
        drawdown = close / peak - 1.0
        decision = (
            "BUY"
            if ma20 > ma50 > ma100
            and drawdown >= -0.12
            else "HOLD"
        )
        return _result(
            name,
            decision,
            abs(drawdown) * 5.0
            + abs(ma20 - ma100) / max(close, 1.0) * 5.0,
            "trend_with_drawdown_filter",
        )

    if name == "Volatility Contraction Pattern":
        prior_volatility = pstdev(daily_returns[-40:-20])
        decision = (
            "BUY"
            if current_volatility < prior_volatility
            and close > max(highs[-6:-1])
            else "HOLD"
        )
        return _result(
            name,
            decision,
            abs(prior_volatility - current_volatility) * 30.0,
            "volatility_contraction_breakout",
        )

    if name == "Volatility Managed Momentum":
        score = momentum20 / max(current_volatility, 1e-9)
        return _result(
            name,
            "BUY" if score > 0.0 else "SELL",
            abs(score) / 10.0,
            "volatility_managed_momentum",
        )

    if name == "Volatility Regime Switching":
        ratio = current_volatility / long_volatility
        decision = (
            "BUY" if ma20 > ma50 and ratio <= 1.25
            else "SELL" if ma20 < ma50 and ratio >= 1.25
            else "HOLD"
        )
        return _result(
            name,
            decision,
            abs(ratio - 1.0),
            "trend_volatility_regime_switch",
        )

    if name == "Volatility-Scaled Momentum":
        score = _returns(closes, 60) / max(current_volatility, 1e-9)
        return _result(
            name,
            "BUY" if score > 0.0 else "SELL",
            abs(score) / 12.0,
            "sixty_day_volatility_scaled_momentum",
        )

    if name == "Volatility-Scaled Trend":
        spread = (ma20 - ma50) / max(abs(ma50), 1.0)
        score = spread / max(current_volatility, 1e-9)
        return _result(
            name,
            "BUY" if score > 0.0 else "SELL",
            abs(score) / 10.0,
            "volatility_scaled_moving_average_trend",
        )

    return _abstain(name, "unsupported_v8_strategy")


def _make_evaluator(name: str) -> Callable[[Sequence[object]], Result]:
    def evaluator(bars: Sequence[object]) -> Result:
        return _evaluate(name, bars)

    evaluator.__name__ = "evaluate_" + (
        name.lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    return evaluator


BULK_OFFLINE_EVALUATORS_V8 = {
    name: _make_evaluator(name)
    for name in EIGHTH_FIFTEEN_STRICT_OHLCV_NAMES
}


def healthcheck() -> dict[str, object]:
    return {
        "status": "ok",
        "strategy_count": 15,
        "offline_only": True,
        "registry_activated": False,
        "execution_enabled": False,
    }
