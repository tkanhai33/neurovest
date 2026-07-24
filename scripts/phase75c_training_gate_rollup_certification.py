#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

PHASE = "75C_TRAINING_GATE_ROLLUP_CERTIFICATION"

EXPECTED = {
    "74A_training_architecture": ARCH / "learning_training_architecture/74A_learning_training_architecture_planning_latest.json",
    "75A_training_gate_stub": ARCH / "training_gate_stub/75A_training_gate_stub_latest.json",
    "75B_training_gate_certification": ARCH / "training_gate_certification/75B_training_gate_certification_latest.json",
}

OUT_DIR = ARCH / "training_gate_rollup"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "75C_training_gate_rollup_certification_latest.json"
OUT_TXT = OUT_DIR / "75C_training_gate_rollup_certification_latest.txt"


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

cert = read_json(EXPECTED["75B_training_gate_certification"])
status = cert.get("training_gate_status", {})

checks["status_present"] = bool(status)
checks["training_disabled"] = status.get("training_enabled") is False
checks["self_mutation_blocked"] = status.get("self_mutation_allowed") is False
checks["autonomous_promotion_blocked"] = status.get("autonomous_promotion_allowed") is False
checks["strategy_db_write_blocked"] = status.get("strategy_db_write_allowed") is False
checks["broker_live_blocked"] = (
    status.get("broker_execution_enabled") is False
    and status.get("live_execution_enabled") is False
)

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "TRAINING_GATE_ROLLUP_CERTIFICATION",
    "artifacts": artifacts,
    "training_gate_status": status,
    "policy": {
        "training_gate_rollup_certified": True,
        "training_enabled": False,
        "self_mutation_allowed": False,
        "autonomous_promotion_allowed": False,
        "strategy_db_write_allowed": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": checks,
    "recommended_next_phase": "76A_REPLAY_TO_TRAINING_SAFETY_ROLLUP",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        "",
        "Training gate status:",
        *[f"- {k}: {v}" for k, v in status.items()],
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
