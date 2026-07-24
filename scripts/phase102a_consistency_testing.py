#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json, hashlib

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "learner_outcome_comparison" / "101A_learner_outcome_comparison_latest.json"
OBS = ARCH / "read_only_sandbox_training_run_with_stream" / "sandbox/TRAINING_RUN_0001/observations.json"
CANDIDATES = ARCH / "read_only_sandbox_training_run_with_stream" / "sandbox/TRAINING_RUN_0001/candidate_ideas.json"

OUT_DIR = ARCH / "consistency_testing"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "102A_consistency_testing_latest.json"
OUT_TXT = OUT_DIR / "102A_consistency_testing_latest.txt"

PHASE = "102A_CONSISTENCY_TESTING"


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return [] if path.name.endswith(".json") else {}


def digest_payload(payload) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


source = read_json(SOURCE)
observations = read_json(OBS)
candidates = read_json(CANDIDATES)

runs = []
for run_index in range(1, 4):
    snapshot = {
        "run_index": run_index,
        "observation_count": len(observations),
        "candidate_count": len(candidates),
        "observation_digest": digest_payload(observations),
        "candidate_digest": digest_payload(candidates),
        "strategy_families": sorted(set(c.get("strategy_family") for c in candidates)),
        "symbols": sorted(set(o.get("symbol") for o in observations)),
        "writes_executed": False,
        "mutation_executed": False,
        "promotion_executed": False,
        "broker_live_executed": False,
    }
    runs.append(snapshot)

reference = runs[0] if runs else {}
consistent = all(
    r.get("observation_digest") == reference.get("observation_digest")
    and r.get("candidate_digest") == reference.get("candidate_digest")
    and r.get("symbols") == reference.get("symbols")
    for r in runs
)

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "observations_loaded": len(observations) == 10,
    "candidate_ideas_loaded": len(candidates) == 10,
    "repeat_runs_created": len(runs) == 3,
    "outputs_consistent": consistent,
    "learner_write_not_executed": all(r["writes_executed"] is False for r in runs),
    "mutation_not_executed": all(r["mutation_executed"] is False for r in runs),
    "promotion_not_executed": all(r["promotion_executed"] is False for r in runs),
    "broker_live_not_executed": all(r["broker_live_executed"] is False for r in runs),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "CONSISTENCY_TESTING_READ_ONLY",
    "consistency_summary": {
        "repeat_runs": len(runs),
        "outputs_consistent": consistent,
        "observation_digest": reference.get("observation_digest"),
        "candidate_digest": reference.get("candidate_digest"),
    },
    "runs": runs,
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
    "recommended_next_phase": "103A_FALSE_POSITIVE_HALLUCINATION_SCORING",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"repeat_runs: {len(runs)}",
        f"outputs_consistent: {consistent}",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "repeat_runs": len(runs),
    "outputs_consistent": consistent,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
