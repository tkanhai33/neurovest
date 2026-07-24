#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "replay_to_training_safety_rollup" / "76A_replay_to_training_safety_rollup_latest.json"

OUT_DIR = ARCH / "training_precondition_gap_manifest"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "76B_training_precondition_gap_manifest_latest.json"
OUT_TXT = OUT_DIR / "76B_training_precondition_gap_manifest_latest.txt"

PHASE = "76B_TRAINING_PRECONDITION_GAP_MANIFEST"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)

gaps = [
    {
        "gap_id": "GAP_001",
        "name": "historical_replay_on_real_bar_data",
        "status": "MISSING",
        "required_before_training": True,
        "recommended_phase": "77A_REAL_HISTORICAL_REPLAY_DRY_RUN_ARCHITECTURE",
    },
    {
        "gap_id": "GAP_002",
        "name": "stress_test_report_store",
        "status": "MISSING",
        "required_before_training": True,
        "recommended_phase": "78A_STRESS_TEST_REPORT_STORE",
    },
    {
        "gap_id": "GAP_003",
        "name": "manual_activation_gate",
        "status": "MISSING",
        "required_before_training": True,
        "recommended_phase": "79A_MANUAL_ACTIVATION_GATE_STUB",
    },
    {
        "gap_id": "GAP_004",
        "name": "near_miss_refactor_queue_capped_at_3",
        "status": "MISSING",
        "required_before_training": True,
        "recommended_phase": "80A_NEAR_MISS_REFACTOR_QUEUE_STUB",
    },
    {
        "gap_id": "GAP_005",
        "name": "quarantine_or_trash_path",
        "status": "MISSING",
        "required_before_training": True,
        "recommended_phase": "81A_CANDIDATE_QUARANTINE_TRASH_PATH",
    },
    {
        "gap_id": "GAP_006",
        "name": "training_read_only_learner_stub",
        "status": "MISSING",
        "required_before_training": True,
        "recommended_phase": "82A_TRAINING_READ_ONLY_LEARNER_STUB",
    },
]

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "gap_manifest_present": len(gaps) > 0,
    "all_gaps_required_before_training": all(g["required_before_training"] is True for g in gaps),
    "training_still_blocked": source.get("safety_rollup", {}).get("safe_to_enable_training_now") is False,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "TRAINING_PRECONDITION_GAP_MANIFEST",
    "source_safety_rollup": str(SOURCE),
    "safe_to_enable_training_now": False,
    "gaps": gaps,
    "policy": {
        "training_precondition_manifest_allowed": True,
        "training_enabled": False,
        "self_mutation_allowed": False,
        "autonomous_promotion_allowed": False,
        "strategy_db_write_allowed": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": checks,
    "recommended_next_phase": "77A_REAL_HISTORICAL_REPLAY_DRY_RUN_ARCHITECTURE",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"safe_to_enable_training_now: {result['safe_to_enable_training_now']}",
        "",
        "Missing before training:",
        *[f"- {g['gap_id']}: {g['name']} -> {g['recommended_phase']}" for g in gaps],
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "gap_count": len(gaps),
    "safe_to_enable_training_now": result["safe_to_enable_training_now"],
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
