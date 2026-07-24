#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()

SANDBOX_DIR = ROOT / "backend/app/stacks/strategy_candidate_sandbox"
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)

SCORECARD = SANDBOX_DIR / "candidate_scorecard_from_replay_metrics.py"

OUT_DIR = ROOT / "runtime/strategy_candidate_sandbox"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT = OUT_DIR / "32B_candidate_scorecard_from_replay_metrics_latest.json"
PHASE = "32B_CANDIDATE_SCORECARD_FROM_REPLAY_METRICS"

SCORECARD.write_text('''from __future__ import annotations

from typing import Any


SAFETY_LOCKS = {
    "live_execution_enabled": False,
    "broker_execution_enabled": False,
    "historical_replay_enabled": False,
    "simulation_enabled": False,
    "registry_write_enabled": False,
    "promotion_enabled": False,
    "learning_enabled": False,
}


def _num(value: Any) -> float | None:
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def build_candidate_scorecard(metrics: dict[str, Any]) -> dict[str, Any]:
    total_return = _num(metrics.get("total_return_pct"))
    max_drawdown = _num(metrics.get("max_drawdown_pct"))
    volatility = _num(metrics.get("volatility_pct"))

    score = 0

    if total_return is not None:
        score += max(min(total_return * 5, 40), -40)

    if max_drawdown is not None:
        score += max(30 + max_drawdown * 3, 0)

    if volatility is not None:
        score += max(20 - volatility, 0)

    score = round(max(min(score, 100), 0), 4)

    if score >= 70:
        rating = "review_candidate"
    elif score >= 40:
        rating = "weak_candidate"
    else:
        rating = "reject_candidate"

    return {
        "candidate_id": metrics.get("candidate_id"),
        "symbol": metrics.get("symbol"),
        "provider": metrics.get("provider"),
        "scorecard_generated": True,
        "scorecard_mode": "metrics_review_only_no_promotion",
        "score": score,
        "rating": rating,
        "inputs": {
            "metrics_mode": metrics.get("metrics_mode"),
            "bars_used": metrics.get("bars_used"),
            "total_return_pct": total_return,
            "max_drawdown_pct": max_drawdown,
            "volatility_pct": volatility,
            "trades_simulated": metrics.get("trades_simulated"),
        },
        "decision": {
            "eligible_for_manual_review": rating == "review_candidate",
            "eligible_for_promotion": False,
            "promotion_attempted": False,
            "registry_written": False,
            "learning_attempted": False,
            "broker_execution_attempted": False,
            "live_execution_attempted": False,
        },
        "safety_locks": SAFETY_LOCKS.copy(),
    }


def validate_candidate_scorecard(scorecard: dict[str, Any]) -> dict[str, Any]:
    decision = scorecard.get("decision", {}) if isinstance(scorecard, dict) else {}

    checks = {
        "scorecard_is_dict": isinstance(scorecard, dict),
        "scorecard_generated_true": scorecard.get("scorecard_generated") is True,
        "scorecard_mode_review_only": scorecard.get("scorecard_mode") == "metrics_review_only_no_promotion",
        "score_numeric": isinstance(scorecard.get("score"), (int, float)),
        "rating_present": scorecard.get("rating") in {"review_candidate", "weak_candidate", "reject_candidate"},
        "eligible_for_promotion_false": decision.get("eligible_for_promotion") is False,
        "promotion_not_attempted": decision.get("promotion_attempted") is False,
        "registry_not_written": decision.get("registry_written") is False,
        "learning_not_attempted": decision.get("learning_attempted") is False,
        "broker_execution_not_attempted": decision.get("broker_execution_attempted") is False,
        "live_execution_not_attempted": decision.get("live_execution_attempted") is False,
        "all_safety_locks_false": all(v is False for v in scorecard.get("safety_locks", {}).values()),
    }

    return {
        "status": "ok" if all(checks.values()) else "failed",
        "checks": checks,
        "certified": all(checks.values()),
    }
''', encoding="utf-8")

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "created_file": str(SCORECARD),
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    import py_compile
    py_compile.compile(str(SCORECARD), doraise=True)

    from backend.app.stacks.market_data.yfinance_historical_bars_adapter import get_historical_bars
    from backend.app.stacks.strategy_candidate_sandbox.replay_metrics_generator import generate_bar_only_metrics
    from backend.app.stacks.strategy_candidate_sandbox.candidate_scorecard_from_replay_metrics import (
        build_candidate_scorecard,
        validate_candidate_scorecard,
    )

    bars_response = get_historical_bars("AAPL", "2024-01-01", "2024-02-01", "1d")
    bars = bars_response.get("bars") if isinstance(bars_response, dict) else []

    metrics = generate_bar_only_metrics(
        candidate_id="candidate_31e_stub_001",
        symbol="AAPL",
        provider="yfinance",
        bars=bars,
    )

    scorecard = build_candidate_scorecard(metrics)
    validation = validate_candidate_scorecard(scorecard)

    result["metrics_summary"] = {
        "metrics_generated": metrics.get("metrics_generated"),
        "metrics_mode": metrics.get("metrics_mode"),
        "bars_used": metrics.get("bars_used"),
        "total_return_pct": metrics.get("total_return_pct"),
        "max_drawdown_pct": metrics.get("max_drawdown_pct"),
        "volatility_pct": metrics.get("volatility_pct"),
        "trades_simulated": metrics.get("trades_simulated"),
    }
    result["scorecard"] = scorecard
    result["validation"] = validation

    decision = scorecard.get("decision", {})

    result["checks"]["scorecard_file_exists"] = SCORECARD.exists()
    result["checks"]["scorecard_compiles"] = True
    result["checks"]["metrics_generated_true"] = metrics.get("metrics_generated") is True
    result["checks"]["metrics_mode_bar_only"] = metrics.get("metrics_mode") == "bar_only_no_trades"
    result["checks"]["scorecard_generated_true"] = scorecard.get("scorecard_generated") is True
    result["checks"]["validation_certified"] = validation.get("certified") is True
    result["checks"]["trades_simulated_zero"] = metrics.get("trades_simulated") == 0
    result["checks"]["eligible_for_promotion_false"] = decision.get("eligible_for_promotion") is False
    result["checks"]["promotion_not_attempted"] = decision.get("promotion_attempted") is False
    result["checks"]["registry_not_written"] = decision.get("registry_written") is False
    result["checks"]["learning_not_attempted"] = decision.get("learning_attempted") is False
    result["checks"]["broker_execution_not_attempted"] = decision.get("broker_execution_attempted") is False
    result["checks"]["live_execution_not_attempted"] = decision.get("live_execution_attempted") is False
    result["checks"]["all_safety_locks_false"] = all(v is False for v in scorecard.get("safety_locks", {}).values())

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(json.dumps(result, indent=2))
print(f"\nWROTE: {OUT}")
