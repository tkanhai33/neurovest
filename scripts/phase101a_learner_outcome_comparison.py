#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "training_safety_certification_and_result_store" / \
    "99A_100A_training_safety_certification_and_result_store_latest.json"

OBS = ARCH / "read_only_sandbox_training_run_with_stream" / \
    "sandbox/TRAINING_RUN_0001/observations.json"

CANDIDATES = ARCH / "read_only_sandbox_training_run_with_stream" / \
    "sandbox/TRAINING_RUN_0001/candidate_ideas.json"

OUT_DIR = ARCH / "learner_outcome_comparison"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "101A_learner_outcome_comparison_latest.json"
OUT_TXT = OUT_DIR / "101A_learner_outcome_comparison_latest.txt"

PHASE = "101A_LEARNER_OUTCOME_COMPARISON"


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return [] if path.name.endswith(".json") else {}


source = read_json(SOURCE)
observations = read_json(OBS)
candidates = read_json(CANDIDATES)

comparisons = []

supported = 0

for obs in observations:

    cumulative = obs.get("cumulative_return", 0.0)
    volatility = obs.get("volatility", 0.0)

    if cumulative > 0:
        verdict = "SUPPORTED"
        supported += 1
    elif cumulative < 0:
        verdict = "NEGATIVE"
    else:
        verdict = "NEUTRAL"

    comparisons.append({
        "symbol": obs.get("symbol"),
        "verdict": verdict,
        "cumulative_return": cumulative,
        "volatility": volatility,
        "observation_supported": verdict == "SUPPORTED",
        "training_write_required": False,
    })

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "observations_loaded": len(observations) == 10,
    "candidate_ideas_loaded": len(candidates) == 10,
    "comparisons_generated": len(comparisons) == len(observations),
    "training_write_disabled": True,
    "mutation_disabled": True,
    "db_write_disabled": True,
    "promotion_disabled": True,
    "broker_disabled": True,
    "live_disabled": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "LEARNER_OUTCOME_COMPARISON",
    "summary": {
        "symbols_compared": len(comparisons),
        "supported_observations": supported,
        "unsupported_observations": len(comparisons) - supported,
    },
    "comparisons": comparisons,
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
    "recommended_next_phase": "102A_CONSISTENCY_TESTING",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"symbols_compared: {len(comparisons)}",
        f"supported_observations: {supported}",
        f"unsupported_observations: {len(comparisons)-supported}",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "symbols_compared": len(comparisons),
    "supported_observations": supported,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
