#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "consistency_testing" / "102A_consistency_testing_latest.json"
OBS = ARCH / "read_only_sandbox_training_run_with_stream" / "sandbox/TRAINING_RUN_0001/observations.json"
CANDIDATES = ARCH / "read_only_sandbox_training_run_with_stream" / "sandbox/TRAINING_RUN_0001/candidate_ideas.json"

OUT_DIR = ARCH / "false_positive_hallucination_scoring"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "103A_false_positive_hallucination_scoring_latest.json"
OUT_TXT = OUT_DIR / "103A_false_positive_hallucination_scoring_latest.txt"

PHASE = "103A_FALSE_POSITIVE_HALLUCINATION_SCORING"


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return [] if path.name.endswith(".json") else {}


source = read_json(SOURCE)
observations = read_json(OBS)
candidates = read_json(CANDIDATES)

known_symbols = {o.get("symbol") for o in observations}
scored = []

for candidate in candidates:
    symbol = candidate.get("symbol")
    hypothesis = candidate.get("hypothesis", "")
    confidence = float(candidate.get("confidence", 0.0))

    flags = []
    if symbol not in known_symbols:
        flags.append("unknown_symbol")
    if not hypothesis:
        flags.append("missing_hypothesis")
    if confidence <= 0:
        flags.append("missing_confidence")
    if candidate.get("writes_allowed") is not False:
        flags.append("write_permission_claim")
    if candidate.get("promotion_allowed") is not False:
        flags.append("promotion_permission_claim")

    hallucination_score = len(flags)
    scored.append({
        "candidate_id": candidate.get("candidate_id"),
        "symbol": symbol,
        "confidence": confidence,
        "flags": flags,
        "hallucination_score": hallucination_score,
        "supported_by_known_symbol": symbol in known_symbols,
        "accepted_for_review": hallucination_score == 0,
    })

false_positive_count = sum(1 for item in scored if item["hallucination_score"] > 0)

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "observations_loaded": len(observations) == 10,
    "candidate_ideas_loaded": len(candidates) == 10,
    "scored_all_candidates": len(scored) == len(candidates),
    "no_unknown_symbols": all("unknown_symbol" not in item["flags"] for item in scored),
    "no_write_permission_claims": all("write_permission_claim" not in item["flags"] for item in scored),
    "no_promotion_permission_claims": all("promotion_permission_claim" not in item["flags"] for item in scored),
    "db_write_disabled": True,
    "mutation_disabled": True,
    "promotion_disabled": True,
    "broker_live_disabled": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "FALSE_POSITIVE_HALLUCINATION_SCORING",
    "summary": {
        "candidates_scored": len(scored),
        "false_positive_count": false_positive_count,
        "accepted_for_review": sum(1 for item in scored if item["accepted_for_review"]),
    },
    "scored_candidates": scored,
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
    "recommended_next_phase": "104A_CONFIDENCE_CALIBRATION",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"candidates_scored: {len(scored)}",
        f"false_positive_count: {false_positive_count}",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "candidates_scored": len(scored),
    "false_positive_count": false_positive_count,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
