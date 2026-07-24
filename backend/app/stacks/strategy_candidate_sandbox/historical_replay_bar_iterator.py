from __future__ import annotations

from typing import Any, Iterator


SAFETY_LOCKS = {
    "live_execution_enabled": False,
    "broker_execution_enabled": False,
    "historical_replay_enabled": False,
    "simulation_enabled": False,
    "registry_write_enabled": False,
    "promotion_enabled": False,
    "learning_enabled": False,
}


def valid_bar(bar: dict[str, Any]) -> bool:
    if not isinstance(bar, dict):
        return False

    required = ["timestamp", "open", "high", "low", "close"]

    if not all(k in bar for k in required):
        return False

    for key in ["open", "high", "low", "close"]:
        value = bar.get(key)
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return False

    volume = bar.get("volume")
    if volume is not None and (not isinstance(volume, (int, float)) or isinstance(volume, bool)):
        return False

    return True


def iter_replay_bars(bars: list[dict[str, Any]]) -> Iterator[dict[str, Any]]:
    """
    Phase 31D bar iterator only.

    This only yields validated bar envelopes.
    It does not simulate trades, generate metrics, write registries,
    promote candidates, learn, or call brokers.
    """
    if not isinstance(bars, list):
        return

    for index, bar in enumerate(bars):
        if not valid_bar(bar):
            continue

        yield {
            "index": index,
            "timestamp": bar["timestamp"],
            "bar": {
                "open": bar["open"],
                "high": bar["high"],
                "low": bar["low"],
                "close": bar["close"],
                "volume": bar.get("volume"),
            },
            "actions": {
                "trade_simulated": False,
                "metrics_generated": False,
                "scorecard_generated": False,
                "registry_written": False,
                "promotion_attempted": False,
                "learning_attempted": False,
            },
        }


def summarize_bar_iteration(bars: list[dict[str, Any]]) -> dict[str, Any]:
    yielded = list(iter_replay_bars(bars))

    return {
        "status": "ok",
        "bars_input": len(bars) if isinstance(bars, list) else 0,
        "bars_yielded": len(yielded),
        "first": yielded[0] if yielded else None,
        "last": yielded[-1] if yielded else None,
        "safety_locks": SAFETY_LOCKS.copy(),
        "actions": {
            "trade_simulated": False,
            "metrics_generated": False,
            "scorecard_generated": False,
            "registry_written": False,
            "promotion_attempted": False,
            "learning_attempted": False,
        },
    }
