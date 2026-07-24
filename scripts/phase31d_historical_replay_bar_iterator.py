#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()

SANDBOX_DIR = ROOT / "backend/app/stacks/strategy_candidate_sandbox"
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)

ITERATOR = SANDBOX_DIR / "historical_replay_bar_iterator.py"

OUT_DIR = ROOT / "runtime/strategy_candidate_sandbox"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT = OUT_DIR / "31D_historical_replay_bar_iterator_latest.json"
PHASE = "31D_HISTORICAL_REPLAY_BAR_ITERATOR"

ITERATOR.write_text('''from __future__ import annotations

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
''', encoding="utf-8")

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "created_file": str(ITERATOR),
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    import py_compile
    py_compile.compile(str(ITERATOR), doraise=True)

    from backend.app.stacks.market_data.yfinance_historical_bars_adapter import get_historical_bars
    from backend.app.stacks.strategy_candidate_sandbox.historical_replay_bar_iterator import (
        summarize_bar_iteration,
        SAFETY_LOCKS,
    )

    bars_response = get_historical_bars("AAPL", "2024-01-01", "2024-02-01", "1d")
    bars = bars_response.get("bars") if isinstance(bars_response, dict) else []

    summary = summarize_bar_iteration(bars)

    result["provider_status"] = bars_response.get("status") if isinstance(bars_response, dict) else None
    result["provider_bar_count"] = len(bars) if isinstance(bars, list) else 0
    result["iterator_summary"] = summary

    actions = summary.get("actions", {})

    result["checks"]["iterator_file_exists"] = ITERATOR.exists()
    result["checks"]["iterator_compiles"] = True
    result["checks"]["provider_returned_bars"] = isinstance(bars, list) and len(bars) > 0
    result["checks"]["summary_status_ok"] = summary.get("status") == "ok"
    result["checks"]["bars_yielded_gt_zero"] = summary.get("bars_yielded", 0) > 0
    result["checks"]["bars_yielded_not_more_than_input"] = summary.get("bars_yielded", 0) <= summary.get("bars_input", 0)
    result["checks"]["first_bar_exists"] = isinstance(summary.get("first"), dict)
    result["checks"]["last_bar_exists"] = isinstance(summary.get("last"), dict)
    result["checks"]["trade_not_simulated"] = actions.get("trade_simulated") is False
    result["checks"]["metrics_not_generated"] = actions.get("metrics_generated") is False
    result["checks"]["scorecard_not_generated"] = actions.get("scorecard_generated") is False
    result["checks"]["registry_not_written"] = actions.get("registry_written") is False
    result["checks"]["promotion_not_attempted"] = actions.get("promotion_attempted") is False
    result["checks"]["learning_not_attempted"] = actions.get("learning_attempted") is False
    result["checks"]["all_safety_locks_false"] = all(v is False for v in SAFETY_LOCKS.values())

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(json.dumps(result, indent=2))
print(f"\nWROTE: {OUT}")
