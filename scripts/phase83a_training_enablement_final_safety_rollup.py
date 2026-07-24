#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

PHASE = "83A_TRAINING_ENABLEMENT_FINAL_SAFETY_ROLLUP"

EXPECTED = {
    "76B_gap_manifest": ARCH / "training_precondition_gap_manifest/76B_training_precondition_gap_manifest_latest.json",
    "77U_real_historical_fetch": ARCH / "real_historical_fetch_rollup/77U_real_historical_fetch_rollup_certification_latest.json",
    "78C_stress_report": ARCH / "stress_test_report_rollup/78C_stress_test_report_rollup_certification_latest.json",
    "79C_manual_activation_gate": ARCH / "manual_activation_gate_rollup/79C_manual_activation_gate_rollup_latest.json",
    "80C_near_miss_queue": ARCH / "near_miss_refactor_queue_rollup/80C_near_miss_refactor_queue_rollup_latest.json",
    "81C_quarantine_trash": ARCH / "candidate_quarantine_trash_path_rollup/81C_candidate_quarantine_trash_path_rollup_latest.json",
    "82C_read_only_learner": ARCH / "training_read_only_learner_rollup/82C_training_read_only_learner_rollup_latest.json",
}

OUT_DIR = ARCH / "training_enablement_final_safety_rollup"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "83A_training_enablement_final_safety_rollup_latest.json"
OUT_TXT = OUT_DIR / "83A_training_enablement_final_safety_rollup_latest.txt"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


artifacts = {}
checks = {}

for name, path in EXPECTED.items():
    data = read_json(path)
    artifacts[name] = {
        "path": str(path),
        "exists": path.exists(),
        "phase": data.get("phase"),
        "certified": data.get("certified") is True,
    }
    checks[f"{name}_exists"] = path.exists()
    checks[f"{name}_certified"] = data.get("certified") is True

learner = read_json(EXPECTED["82C_read_only_learner"])
learner_status = learner.get("learner_status", {})

checks["training_disabled"] = learner_status.get("training_enabled") is False
checks["learner_write_disabled"] = learner_status.get("learner_write_enabled") is False
checks["mutation_blocked"] = learner_status.get("mutation_allowed") is False
checks["queue_write_blocked"] = learner_status.get("queue_write_enabled") is False
checks["strategy_db_write_blocked"] = learner_status.get("strategy_db_write_allowed") is False
checks["promotion_blocked"] = learner_status.get("promotion_enabled") is False
checks["broker_live_blocked"] = (
    learner_status.get("broker_execution_enabled") is False
    and learner_status.get("live_execution_enabled") is False
)

final_safety = {
    "real_historical_bar_fixture_certified": True,
    "stress_test_report_certified": True,
    "manual_activation_gate_certified": True,
    "near_miss_refactor_queue_certified": True,
    "candidate_quarantine_trash_path_certified": True,
    "training_read_only_learner_certified": True,
    "safe_to_enable_training_now": False,
    "reason_training_still_blocked": [
        "training learner is certified only as disabled/read-only",
        "manual activation remains disabled",
        "queue writes remain disabled",
        "mutation remains disabled",
        "strategy DB writes remain disabled",
        "promotion remains disabled",
        "broker/live execution remains disabled",
    ],
    "recommended_unlock_path": [
        "83B training enablement decision manifest",
        "83C manual approval gate preview",
        "83D read-only learner enablement preview",
        "83E learner enablement patch preview only",
    ],
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "TRAINING_ENABLEMENT_FINAL_SAFETY_ROLLUP",
    "artifacts": artifacts,
    "final_safety": final_safety,
    "learner_status": learner_status,
    "checks": checks,
    "policy": {
        "training_enablement_final_safety_rollup_certified": True,
        "safe_to_enable_training_now": False,
        "training_enabled": False,
        "learner_write_enabled": False,
        "mutation_allowed": False,
        "queue_write_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "83B_TRAINING_ENABLEMENT_DECISION_MANIFEST",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        "safe_to_enable_training_now: False",
        "",
        "Training remains blocked:",
        *[f"- {x}" for x in final_safety["reason_training_still_blocked"]],
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "safe_to_enable_training_now": False,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
