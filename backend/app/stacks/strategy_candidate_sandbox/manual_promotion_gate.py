from __future__ import annotations

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
