"""Fifth qualified batch: deterministic single-symbol OHLCV strategies."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from math import isfinite
from statistics import mean
from typing import Any, Callable

Result = dict[str, object]

FIFTH_FIFTEEN_OHLCV_NAMES = (
    "12-1 Momentum",
    "52-Week High Momentum",
    "Adaptive Mean Reversion",
    "Adaptive Trend Following",
    "Bollinger Squeeze",
    "Breakout Pullback",
    "Chandelier Exit Trend",
    "Darvas Box",
    "Donchian Breakout with ATR Sizing",
    "Ease of Movement",
    "Force Index",
    "Moving Average Pullback",
    "Price Volume Trend",
    "Range Expansion",
    "Turtle Trading Breakout",
)


def _value(bar: object, field: str) -> float:
    raw = bar.get(field) if isinstance(bar, Mapping) else getattr(bar, field)
    value = float(raw)
    if not isfinite(value):
        raise ValueError(f"{field} must be finite")
    return value


def _series(bars: Sequence[object], field: str) -> list[float]:
    return [_value(bar, field) for bar in bars]


def _result(
    name: str,
    decision: str,
    confidence: float,
    reason: str,
) -> Result:
    decision = decision if decision in {"BUY", "SELL", "HOLD"} else "HOLD"
    return {
        "status": "ok",
        "strategy_name": name,
        "evaluator_id": (
            name.lower()
            .replace("-", "_")
            .replace(" ", "_")
            .replace("/", "_")
            + "_v1"
        ),
        "decision": decision,
        "signal": decision,
        "confidence": round(min(max(confidence, 0.0), 1.0), 6),
        "reason": reason,
        "execution_enabled": False,
    }


def _abstain(name: str, reason: str) -> Result:
    return {
        "status": "abstain",
        "strategy_name": name,
        "evaluator_id": (
            name.lower()
            .replace("-", "_")
            .replace(" ", "_")
            .replace("/", "_")
            + "_v1"
        ),
        "decision": "ABSTAIN",
        "signal": "ABSTAIN",
        "confidence": 0.0,
        "reason": reason,
        "execution_enabled": False,
    }


def _ema(values: Sequence[float], period: int) -> float:
    alpha = 2.0 / (period + 1.0)
    value = values[0]
    for point in values[1:]:
        value = alpha * point + (1.0 - alpha) * value
    return value


def _atr(highs: Sequence[float], lows: Sequence[float], closes: Sequence[float], period: int = 20) -> float:
    if len(closes) < period + 1:
        return 0.0
    ranges = [
        max(
            highs[index] - lows[index],
            abs(highs[index] - closes[index - 1]),
            abs(lows[index] - closes[index - 1]),
        )
        for index in range(1, len(closes))
    ]
    return mean(ranges[-period:])


def _evaluate(name: str, bars: Sequence[object]) -> Result:
    try:
        closes = _series(bars, "close")
        highs = _series(bars, "high")
        lows = _series(bars, "low")
        volumes = _series(bars, "volume")
    except (AttributeError, KeyError, TypeError, ValueError):
        return _abstain(name, "invalid_ohlcv_bars")

    if len(closes) < 60:
        return _abstain(name, "insufficient_ohlcv_history")

    close = closes[-1]
    if close <= 0.0:
        return _abstain(name, "invalid_close")

    ma20 = mean(closes[-20:])
    ma50 = mean(closes[-50:])
    atr20 = _atr(highs, lows, closes)
    range20 = mean(
        high - low for high, low in zip(highs[-20:], lows[-20:], strict=True)
    )

    if name == "12-1 Momentum":
        if len(closes) < 253:
            return _abstain(name, "insufficient_12_1_history")
        momentum = closes[-22] / closes[0] - 1.0
        return _result(name, "BUY" if momentum > 0 else "SELL", abs(momentum), "twelve_one_momentum")

    if name == "52-Week High Momentum":
        if len(highs) < 252:
            return _abstain(name, "insufficient_52_week_history")
        ratio = close / max(highs[-252:])
        return _result(name, "BUY" if ratio >= 0.95 else "HOLD", ratio, "fifty_two_week_high_ratio")

    if name == "Adaptive Mean Reversion":
        deviation = (close - ma20) / max(atr20, close * 0.001)
        decision = "BUY" if deviation <= -1.5 else "SELL" if deviation >= 1.5 else "HOLD"
        return _result(name, decision, min(abs(deviation) / 3.0, 1.0), "atr_normalized_mean_reversion")

    if name == "Adaptive Trend Following":
        fast = _ema(closes[-20:], 10)
        slow = _ema(closes[-50:], 30)
        spread = (fast - slow) / max(abs(slow), 1.0)
        return _result(name, "BUY" if spread > 0 else "SELL", abs(spread) * 100.0, "adaptive_ema_trend")

    if name == "Bollinger Squeeze":
        width = (max(closes[-20:]) - min(closes[-20:])) / ma20
        prior_width = (max(closes[-40:-20]) - min(closes[-40:-20])) / mean(closes[-40:-20])
        decision = "BUY" if width < prior_width and close > ma20 else "SELL" if width < prior_width and close < ma20 else "HOLD"
        return _result(name, decision, abs(prior_width - width) * 10.0, "bollinger_width_compression")

    if name == "Breakout Pullback":
        resistance = max(highs[-21:-1])
        support = min(lows[-10:])
        decision = "BUY" if close > support and close >= resistance * 0.98 else "HOLD"
        return _result(name, decision, abs(close / resistance - 1.0) * 20.0, "breakout_pullback_proximity")

    if name == "Chandelier Exit Trend":
        stop = max(highs[-22:]) - 3.0 * atr20
        return _result(name, "BUY" if close > stop else "SELL", abs(close - stop) / max(close, 1.0) * 10.0, "chandelier_stop_trend")

    if name == "Darvas Box":
        ceiling = max(highs[-21:-1])
        floor = min(lows[-21:-1])
        decision = "BUY" if close > ceiling else "SELL" if close < floor else "HOLD"
        return _result(name, decision, abs(close - (ceiling if decision == "BUY" else floor)) / close * 10.0, "darvas_box_boundary")

    if name == "Donchian Breakout with ATR Sizing":
        ceiling = max(highs[-21:-1])
        floor = min(lows[-21:-1])
        decision = "BUY" if close > ceiling else "SELL" if close < floor else "HOLD"
        return _result(name, decision, atr20 / close * 10.0, "donchian_atr_breakout")

    if name == "Ease of Movement":
        midpoint_moves = [
            ((highs[index] + lows[index]) - (highs[index - 1] + lows[index - 1])) / 2.0
            for index in range(-13, 0)
        ]
        score = sum(
            move / max(volumes[index], 1.0)
            for index, move in zip(range(-13, 0), midpoint_moves, strict=True)
        )
        return _result(name, "BUY" if score > 0 else "SELL", min(abs(score) * 1_000_000.0, 1.0), "ease_of_movement")

    if name == "Force Index":
        force = sum(
            (closes[index] - closes[index - 1]) * volumes[index]
            for index in range(-13, 0)
        )
        return _result(name, "BUY" if force > 0 else "SELL", min(abs(force) / max(sum(volumes[-13:]) * close, 1.0) * 20.0, 1.0), "force_index")

    if name == "Moving Average Pullback":
        decision = "BUY" if close > ma50 and close <= ma20 else "SELL" if close < ma50 and close >= ma20 else "HOLD"
        return _result(name, decision, abs(close - ma20) / close * 10.0, "moving_average_pullback")

    if name == "Price Volume Trend":
        pvt = sum(
            ((closes[index] - closes[index - 1]) / closes[index - 1]) * volumes[index]
            for index in range(-20, 0)
        )
        return _result(name, "BUY" if pvt > 0 else "SELL", min(abs(pvt) / max(sum(volumes[-20:]), 1.0) * 10.0, 1.0), "price_volume_trend")

    if name == "Range Expansion":
        latest_range = highs[-1] - lows[-1]
        decision = "BUY" if latest_range > range20 and close > ma20 else "SELL" if latest_range > range20 and close < ma20 else "HOLD"
        return _result(name, decision, latest_range / max(range20, 1.0) - 1.0, "range_expansion_direction")

    if name == "Turtle Trading Breakout":
        ceiling = max(highs[-56:-1])
        floor = min(lows[-56:-1])
        decision = "BUY" if close > ceiling else "SELL" if close < floor else "HOLD"
        return _result(name, decision, abs(close - (ceiling if decision == "BUY" else floor)) / close * 10.0, "turtle_breakout")

    return _abstain(name, "unsupported_v5_strategy")


def _make_evaluator(name: str) -> Callable[[Sequence[object]], Result]:
    def evaluator(bars: Sequence[object]) -> Result:
        return _evaluate(name, bars)

    evaluator.__name__ = (
        "evaluate_"
        + name.lower().replace("-", "_").replace(" ", "_").replace("/", "_")
    )
    return evaluator


BULK_OFFLINE_EVALUATORS_V5 = {
    name: _make_evaluator(name)
    for name in FIFTH_FIFTEEN_OHLCV_NAMES
}


def healthcheck() -> dict[str, object]:
    return {
        "status": "ok",
        "strategy_count": len(FIFTH_FIFTEEN_OHLCV_NAMES),
        "offline_only": True,
        "registry_activated": False,
        "execution_enabled": False,
    }
