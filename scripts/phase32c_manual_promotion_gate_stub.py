#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()

SANDBOX_DIR = ROOT / "backend/app/stacks/strategy_candidate_sandbox"
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)

GATE = SANDBOX_DIR / "manual_promotion_gate.py"

OUT_DIR = ROOT / "runtime/strategy_candidate_sandbox"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT = OUT_DIR / "32C_manual_promotion_gate_stub_latest.json"
PHASE = "32C_MANUAL_PROMOTION_GATE_STUB"

GATE.write_text('''from __future__ import annotations

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


def evaluate_manual_promotion_gate(scorecard: dict[str, Any]) -> dict[str, Any]:
    decision = scorecard.get("decision", {}) if isinstance(scorecard, dict) else {}

    return {
        "status": "promotion_blocked_stub",
        "reason": "manual_promotion_gate_stub_only",
        "candidate_id": scorecard.get("candidate_id") if isinstance(scorecard, dict) else None,
        "symbol": scorecard.get("symbol") if isinstance(scorecard, dict) else None,
        "score": scorecard.get("score") if isinstance(scorecard, dict) else None,
        "rating": scorecard.get("rating") if isinstance(scorecard, dict) else None,
        "scorecard_eligible_for_manual_review": decision.get("eligible_for_manual_review"),
        "manual_review_recorded": False,
        "manual_approval_recorded": False,
        "eligible_for_promotion": False,
        "promotion_attempted": False,
        "registry_written": False,
        "learning_attempted": False,
        "broker_execution_attempted": False,
        "live_execution_attempted": False,
        "safety_locks": SAFETY_LOCKS.copy(),
    }


def validate_manual_promotion_gate_response(payload: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "payload_is_dict": isinstance(payload, dict),
        "status_blocked_stub": payload.get("status") == "promotion_blocked_stub",
        "manual_review_not_recorded": payload.get("manual_review_recorded") is False,
        "manual_approval_not_recorded": payload.get("manual_approval_recorded") is False,
        "eligible_for_promotion_false": payload.get("eligible_for_promotion") is False,
        "promotion_not_attempted": payload.get("promotion_attempted") is False,
        "registry_not_written": payload.get("registry_written") is False,
        "learning_not_attempted": payload.get("learning_attempted") is False,
        "broker_execution_not_attempted": payload.get("broker_execution_attempted") is False,
        "live_execution_not_attempted": payload.get("live_execution_attempted") is False,
        "all_safety_locks_false": all(v is False for v in payload.get("safety_locks", {}).values()),
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
    "created_file": str(GATE),
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    import py_compile
    py_compile.compile(str(GATE), doraise=True)

    from backend.app.stacks.market_data.yfinance_historical_bars_adapter import get_historical_bars
    from backend.app.stacks.strategy_candidate_sandbox.replay_metrics_generator import generate_bar_only_metrics
    from backend.app.stacks.strategy_candidate_sandbox.candidate_scorecard_from_replay_metrics import build_candidate_scorecard
    from backend.app.stacks.strategy_candidate_sandbox.manual_promotion_gate import (
        evaluate_manual_promotion_gate,
        validate_manual_promotion_gate_response,
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
    gate_response = evaluate_manual_promotion_gate(scorecard)
    validation = validate_manual_promotion_gate_response(gate_response)

    result["scorecard_summary"] = {
        "candidate_id": scorecard.get("candidate_id"),
        "score": scorecard.get("score"),
        "rating": scorecard.get("rating"),
        "eligible_for_manual_review": scorecard.get("decision", {}).get("eligible_for_manual_review"),
        "eligible_for_promotion": scorecard.get("decision", {}).get("eligible_for_promotion"),
    }
    result["gate_response"] = gate_response
    result["validation"] = validation

    result["checks"]["gate_file_exists"] = GATE.exists()
    result["checks"]["gate_compiles"] = True
    result["checks"]["gate_status_blocked_stub"] = gate_response.get("status") == "promotion_blocked_stub"
    result["checks"]["manual_review_not_recorded"] = gate_response.get("manual_review_recorded") is False
    result["checks"]["manual_approval_not_recorded"] = gate_response.get("manual_approval_recorded") is False
    result["checks"]["eligible_for_promotion_false"] = gate_response.get("eligible_for_promotion") is False
    result["checks"]["promotion_not_attempted"] = gate_response.get("promotion_attempted") is False
    result["checks"]["registry_not_written"] = gate_response.get("registry_written") is False
    result["checks"]["learning_not_attempted"] = gate_response.get("learning_attempted") is False
    result["checks"]["broker_execution_not_attempted"] = gate_response.get("broker_execution_attempted") is False
    result["checks"]["live_execution_not_attempted"] = gate_response.get("live_execution_attempted") is False
    result["checks"]["validation_certified"] = validation.get("certified") is True
    result["checks"]["all_safety_locks_false"] = all(v is False for v in gate_response.get("safety_locks", {}).values())

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(json.dumps(result, indent=2))
print(f"\nWROTE: {OUT}")
