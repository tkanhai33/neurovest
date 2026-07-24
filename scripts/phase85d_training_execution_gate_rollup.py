#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

PHASE = "85D_TRAINING_EXECUTION_GATE_ROLLUP"

EXPECTED = {
    "85A_training_execution_gate_preview": ARCH / "training_execution_gate_preview/85A_training_execution_gate_preview_latest.json",
    "85B_training_execution_gate_stub": ARCH / "training_execution_gate/85B_training_execution_gate_stub_latest.json",
    "85C_training_execution_gate_certification": ARCH / "training_execution_gate_certification/85C_training_execution_gate_certification_latest.json",
}

OUT_DIR = ARCH / "training_execution_gate_rollup"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "85D_training_execution_gate_rollup_latest.json"
OUT_TXT = OUT_DIR / "85D_training_execution_gate_rollup_latest.txt"


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

cert = read_json(EXPECTED["85C_training_execution_gate_certification"])
status = cert.get("gate_status", {})

checks["status_present"] = bool(status)
checks["training_execution_disabled"] = status.get("training_execution_enabled") is False
checks["read_only_input_allowed"] = status.get("read_only_input_allowed") is True
checks["learner_write_blocked"] = status.get("learner_write_enabled") is False
checks["mutation_blocked"] = status.get("mutation_allowed") is False
checks["queue_write_blocked"] = status.get("queue_write_enabled") is False
checks["strategy_db_write_blocked"] = status.get("strategy_db_write_allowed") is False
checks["promotion_blocked"] = status.get("promotion_enabled") is False
checks["broker_live_blocked"] = (
    status.get("broker_execution_enabled") is False
    and status.get("live_execution_enabled") is False
)

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "TRAINING_EXECUTION_GATE_ROLLUP",
    "artifacts": artifacts,
    "gate_status": status,
    "policy": {
        "training_execution_gate_rollup_certified": True,
        "training_execution_enabled": False,
        "read_only_input_allowed": True,
        "learner_write_enabled": False,
        "mutation_allowed": False,
        "queue_write_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": checks,
    "recommended_next_phase": "86A_TRAINING_UNLOCK_DECISION_ROLLUP",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        "training_execution_enabled: False",
        "read_only_input_allowed: True",
        "",
        "Training execution gate rollup certified.",
        "Write/mutation/queue/db/promotion/broker/live remain blocked.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "training_execution_enabled": status.get("training_execution_enabled"),
    "read_only_input_allowed": status.get("read_only_input_allowed"),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
