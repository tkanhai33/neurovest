#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json
import math

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "false_positive_hallucination_scoring" / "103A_false_positive_hallucination_scoring_latest.json"
OUTCOME = ARCH / "learner_outcome_comparison" / "101A_learner_outcome_comparison_latest.json"
CANDIDATES = ARCH / "read_only_sandbox_training_run_with_stream" / "sandbox/TRAINING_RUN_0001/candidate_ideas.json"

OUT_DIR = ARCH / "confidence_calibration"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "104A_confidence_calibration_latest.json"
OUT_TXT = OUT_DIR / "104A_confidence_calibration_latest.txt"

PHASE = "104A_CONFIDENCE_CALIBRATION"


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return [] if path.name.endswith(".json") else {}


source = read_json(SOURCE)
outcome = read_json(OUTCOME)
candidates = read_json(CANDIDATES)

comparisons = outcome.get("comparisons", [])
support_by_symbol = {
    item.get("symbol"): bool(item.get("observation_supported"))
    for item in comparisons
}

calibrated = []
abs_errors = []

for candidate in candidates:
    symbol = candidate.get("symbol")
    confidence = float(candidate.get("confidence", 0.0))
    supported = support_by_symbol.get(symbol, False)
    actual = 1.0 if supported else 0.0
    abs_error = abs(confidence - actual)
    abs_errors.append(abs_error)

    calibrated.append({
        "candidate_id": candidate.get("candidate_id"),
        "symbol": symbol,
        "confidence": confidence,
        "actual_supported": supported,
        "absolute_error": abs_error,
        "calibration_band": (
            "well_calibrated" if abs_error <= 0.25 else
            "overconfident" if confidence > actual else
            "underconfident"
        ),
        "writes_allowed": False,
        "promotion_allowed": False,
    })

mean_absolute_error = sum(abs_errors) / len(abs_errors) if abs_errors else None
calibration_score = 1.0 - mean_absolute_error if mean_absolute_error is not None else None

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "outcome_exists": OUTCOME.exists(),
    "outcome_certified": outcome.get("certified") is True,
    "candidates_loaded": len(candidates) == 10,
    "calibrated_all_candidates": len(calibrated) == len(candidates),
    "mean_absolute_error_present": isinstance(mean_absolute_error, float),
    "calibration_score_present": isinstance(calibration_score, float),
    "db_write_disabled": True,
    "mutation_disabled": True,
    "promotion_disabled": True,
    "broker_live_disabled": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "CONFIDENCE_CALIBRATION_READ_ONLY",
    "summary": {
        "candidates_calibrated": len(calibrated),
        "mean_absolute_error": mean_absolute_error,
        "calibration_score": calibration_score,
    },
    "calibrated_candidates": calibrated,
    "checks": checks,
    "policy": {
        "training_execution_enabled": False,
        "learner_write_enabled": False,
        "mutation_allowed": False,
        "queue_write_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "105A_HUMAN_REVIEW_APPROVAL_PACKAGE",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"candidates_calibrated: {len(calibrated)}",
        f"mean_absolute_error: {mean_absolute_error}",
        f"calibration_score: {calibration_score}",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "candidates_calibrated": len(calibrated),
    "mean_absolute_error": mean_absolute_error,
    "calibration_score": calibration_score,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
