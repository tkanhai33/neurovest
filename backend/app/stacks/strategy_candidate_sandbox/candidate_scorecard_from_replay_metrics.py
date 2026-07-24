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
