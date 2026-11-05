"""Deterministic multi-symbol daily-OHLCV evaluators."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from statistics import mean
from typing import Any, Callable

from backend.app.stacks.strategy.evaluators.bulk_indicator_family_v5 import (
    _abstain,
    _result,
)

MULTI_SYMBOL_STRATEGY_NAMES = (
    "Asset Class Momentum",
    "Cross-Asset Trend Confirmation",
    "Relative Strength Sector Rotation",
    "Sector Momentum",
)

_ASSET_ANCHORS = ("SPY", "TLT", "GLD")
_SECTOR_ETFS = (
    "XLK", "XLF", "XLE", "XLV", "XLY", "XLP",
    "XLI", "XLU", "XLB", "XLRE",
)


def _closes(bars: object) -> list[float] | None:
    if isinstance(bars, (str, bytes)) or not isinstance(bars, Sequence):
        return None
    values: list[float] = []
    try:
        for bar in bars:
            value = float(bar["close"])
            if value <= 0.0:
                return None
            values.append(value)
    except (KeyError, TypeError, ValueError):
        return None
    return values


def _return(closes: list[float], days: int) -> float:
    return closes[-1] / closes[-1 - days] - 1.0


def _trend(closes: list[float]) -> int:
    fast = mean(closes[-50:])
    slow = mean(closes[-150:])
    return 1 if fast > slow else -1 if fast < slow else 0


def _evaluate(
    name: str,
    primary_symbol: str,
    universe_bars: Mapping[str, object],
) -> dict[str, object]:
    primary = str(primary_symbol).strip().upper()
    normalized = {
        str(symbol).strip().upper(): _closes(bars)
        for symbol, bars in universe_bars.items()
    }

    if not primary or primary not in normalized or normalized[primary] is None:
        return _abstain(name, "primary_symbol_not_in_owner_universe")

    if any(values is None or len(values) < 253 for values in normalized.values()):
        return _abstain(name, "insufficient_or_invalid_universe_history")

    closes = {symbol: values for symbol, values in normalized.items() if values}

    if name == "Asset Class Momentum":
        if primary not in _ASSET_ANCHORS or not set(_ASSET_ANCHORS) <= set(closes):
            return _abstain(name, "asset_class_anchor_unavailable")
        scores = {symbol: _return(closes[symbol], 126) for symbol in _ASSET_ANCHORS}
        score = scores[primary]
        decision = "BUY" if score == max(scores.values()) and score > 0 else (
            "SELL" if score == min(scores.values()) and score < 0 else "HOLD"
        )
        return _result(name, decision, abs(score) * 6.0, "asset_class_126_day_momentum")

    if name == "Cross-Asset Trend Confirmation":
        if not set(_ASSET_ANCHORS) <= set(closes):
            return _abstain(name, "cross_asset_anchors_unavailable")
        primary_trend = _trend(closes[primary])
        confirmations = sum(_trend(closes[symbol]) for symbol in _ASSET_ANCHORS)
        # Two of the three anchors aligned is sufficient confirmation:
        # (+1 + +1 + -1) == +1, and the inverse is -1.
        decision = "BUY" if primary_trend > 0 and confirmations >= 1 else (
            "SELL" if primary_trend < 0 and confirmations <= -1 else "HOLD"
        )
        return _result(name, decision, abs(confirmations) / 3.0, "cross_asset_trend_confirmation")

    if primary not in _SECTOR_ETFS or not set(_SECTOR_ETFS) <= set(closes):
        return _abstain(name, "sector_universe_unavailable")

    days = 126 if name == "Relative Strength Sector Rotation" else 63
    scores = {symbol: _return(closes[symbol], days) for symbol in _SECTOR_ETFS}
    ordered = sorted(scores, key=scores.get, reverse=True)
    score = scores[primary]
    top = set(ordered[:3])
    bottom = set(ordered[-3:])

    decision = "BUY" if primary in top and score > 0 else (
        "SELL" if primary in bottom and score < 0 else "HOLD"
    )
    reason = (
        "one_hundred_twenty_six_day_sector_relative_strength"
        if days == 126 else "sixty_three_day_sector_momentum"
    )
    return _result(name, decision, abs(score) * 6.0, reason)


def _make(name: str) -> Callable[[str, Mapping[str, object]], dict[str, object]]:
    def evaluator(
        primary_symbol: str,
        universe_bars: Mapping[str, object],
    ) -> dict[str, object]:
        return _evaluate(name, primary_symbol, universe_bars)
    return evaluator


MULTI_SYMBOL_EVALUATORS_V1 = {
    name: _make(name) for name in MULTI_SYMBOL_STRATEGY_NAMES
}


def healthcheck() -> dict[str, object]:
    return {
        "status": "ok",
        "strategy_count": 4,
        "offline_only": True,
        "registry_activated": False,
        "execution_enabled": False,
    }
