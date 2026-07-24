#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

PHASE = "86A_TRAINING_UNLOCK_DECISION_ROLLUP"

EXPECTED = {
    "83A_final_safety": ARCH / "training_enablement_final_safety_rollup/83A_training_enablement_final_safety_rollup_latest.json",
    "83B_decision_manifest": ARCH / "training_enablement_decision_manifest/83B_training_enablement_decision_manifest_latest.json",
    "83H_read_only_learner_enablement": ARCH / "read_only_learner_enablement_rollup/83H_read_only_learner_enablement_rollup_latest.json",
    "84C_read_only_learner_inspection": ARCH / "read_only_learner_inspection_rollup/84C_read_only_learner_inspection_rollup_latest.json",
    "85D_training_execution_gate": ARCH / "training_execution_gate_rollup/85D_training_execution_gate_rollup_latest.json",
}

OUT_DIR = ARCH / "training_unlock_decision_rollup"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "86A_training_unlock_decision_rollup_latest.json"
OUT_TXT = OUT_DIR / "86A_training_unlock_decision_rollup_latest.txt"


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

learner = read_json(EXPECTED["83H_read_only_learner_enablement"])
inspection = read_json(EXPECTED["84C_read_only_learner_inspection"])
gate = read_json(EXPECTED["85D_training_execution_gate"])

learner_status = learner.get("learner_status", {})
gate_status = gate.get("gate_status", {})

unlock_decision = {
    "decision": "DO_NOT_ENABLE_TRAINING_EXECUTION",
    "read_only_learner_enabled": learner_status.get("read_only_learner_enabled") is True,
    "read_only_inspection_certified": inspection.get("certified") is True,
    "training_execution_enabled": gate_status.get("training_execution_enabled") is True,
    "safe_to_enable_training_execution_now": False,
    "why": [
        "read-only learner inspection is certified",
        "training execution gate is certified disabled",
        "learner writes remain disabled",
        "mutation remains disabled",
        "queue writes remain disabled",
        "strategy DB writes remain disabled",
        "promotion remains disabled",
        "broker/live remains disabled",
    ],
}

checks["read_only_learner_enabled"] = unlock_decision["read_only_learner_enabled"] is True
checks["read_only_inspection_certified"] = unlock_decision["read_only_inspection_certified"] is True
checks["training_execution_still_disabled"] = gate_status.get("training_execution_enabled") is False
checks["learner_write_blocked"] = gate_status.get("learner_write_enabled") is False
checks["mutation_blocked"] = gate_status.get("mutation_allowed") is False
checks["queue_write_blocked"] = gate_status.get("queue_write_enabled") is False
checks["strategy_db_write_blocked"] = gate_status.get("strategy_db_write_allowed") is False
checks["promotion_blocked"] = gate_status.get("promotion_enabled") is False
checks["broker_live_blocked"] = (
    gate_status.get("broker_execution_enabled") is False
    and gate_status.get("live_execution_enabled") is False
)
checks["decision_blocks_training_execution"] = unlock_decision["decision"] == "DO_NOT_ENABLE_TRAINING_EXECUTION"

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "TRAINING_UNLOCK_DECISION_ROLLUP",
    "artifacts": artifacts,
    "unlock_decision": unlock_decision,
    "learner_status": learner_status,
    "training_execution_gate_status": gate_status,
    "checks": checks,
    "policy": {
        "training_unlock_decision_rollup_certified": True,
        "read_only_learner_enabled": True,
        "training_execution_enabled": False,
        "learner_write_enabled": False,
        "mutation_allowed": False,
        "queue_write_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "86B_READ_ONLY_TRAINING_SYSTEM_HANDOFF",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"decision: {unlock_decision['decision']}",
        "safe_to_enable_training_execution_now: False",
        "read_only_learner_enabled: True",
        "training_execution_enabled: False",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "decision": unlock_decision["decision"],
    "safe_to_enable_training_execution_now": False,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
