#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "confidence_calibration" / "104A_confidence_calibration_latest.json"
OUTCOME = ARCH / "learner_outcome_comparison" / "101A_learner_outcome_comparison_latest.json"
HALLUCINATION = ARCH / "false_positive_hallucination_scoring" / "103A_false_positive_hallucination_scoring_latest.json"
TRAINING_STORE = ARCH / "training_safety_certification_and_result_store" / "99A_100A_training_safety_certification_and_result_store_latest.json"

OUT_DIR = ARCH / "human_review_approval_package"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "105A_human_review_approval_package_latest.json"
OUT_TXT = OUT_DIR / "105A_human_review_approval_package_latest.txt"

PHASE = "105A_HUMAN_REVIEW_APPROVAL_PACKAGE"


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


confidence = read_json(SOURCE)
outcome = read_json(OUTCOME)
hallucination = read_json(HALLUCINATION)
training_store = read_json(TRAINING_STORE)

review_package = {
    "review_id": "HUMAN_REVIEW_TRAINING_RUN_0001",
    "training_run_id": "TRAINING_RUN_0001",
    "created_at": datetime.now(UTC).isoformat(),
    "review_status": "AWAITING_HUMAN_REVIEW",
    "approval_granted": False,
    "summary": {
        "symbols_compared": outcome.get("summary", {}).get("symbols_compared"),
        "supported_observations": outcome.get("summary", {}).get("supported_observations"),
        "candidates_scored": hallucination.get("summary", {}).get("candidates_scored"),
        "false_positive_count": hallucination.get("summary", {}).get("false_positive_count"),
        "candidates_calibrated": confidence.get("summary", {}).get("candidates_calibrated"),
        "mean_absolute_error": confidence.get("summary", {}).get("mean_absolute_error"),
        "calibration_score": confidence.get("summary", {}).get("calibration_score"),
    },
    "artifacts": {
        "training_store": training_store.get("store"),
        "outcome_comparison": str(OUTCOME),
        "hallucination_scoring": str(HALLUCINATION),
        "confidence_calibration": str(SOURCE),
    },
    "human_review_required_before": [
        "strategy DB writes",
        "candidate promotion",
        "mutation enablement",
        "broker execution",
        "live execution",
    ],
    "hard_blocks": {
        "training_execution_enabled": False,
        "learner_write_enabled": False,
        "mutation_allowed": False,
        "queue_write_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
}

checks = {
    "confidence_source_exists": SOURCE.exists(),
    "confidence_source_certified": confidence.get("certified") is True,
    "outcome_source_exists": OUTCOME.exists(),
    "outcome_source_certified": outcome.get("certified") is True,
    "hallucination_source_exists": HALLUCINATION.exists(),
    "hallucination_source_certified": hallucination.get("certified") is True,
    "training_store_source_exists": TRAINING_STORE.exists(),
    "training_store_source_certified": training_store.get("certified") is True,
    "review_package_present": bool(review_package),
    "approval_not_granted": review_package["approval_granted"] is False,
    "awaiting_human_review": review_package["review_status"] == "AWAITING_HUMAN_REVIEW",
    "strategy_db_write_blocked": review_package["hard_blocks"]["strategy_db_write_allowed"] is False,
    "promotion_blocked": review_package["hard_blocks"]["promotion_enabled"] is False,
    "broker_live_blocked": (
        review_package["hard_blocks"]["broker_execution_enabled"] is False
        and review_package["hard_blocks"]["live_execution_enabled"] is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "HUMAN_REVIEW_APPROVAL_PACKAGE",
    "review_package": review_package,
    "checks": checks,
    "policy": {
        "human_review_package_certified": True,
        **review_package["hard_blocks"],
    },
    "recommended_next_phase": "106A_DEV_TERRITORY_COMMAND_REGISTRY_PREVIEW",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"review_id: {review_package['review_id']}",
        f"review_status: {review_package['review_status']}",
        f"approval_granted: {review_package['approval_granted']}",
        "",
        f"symbols_compared: {review_package['summary']['symbols_compared']}",
        f"supported_observations: {review_package['summary']['supported_observations']}",
        f"false_positive_count: {review_package['summary']['false_positive_count']}",
        f"calibration_score: {review_package['summary']['calibration_score']}",
        "",
        "Human review required before DB writes, promotion, mutation, broker, or live execution.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "review_status": review_package["review_status"],
    "approval_granted": review_package["approval_granted"],
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
