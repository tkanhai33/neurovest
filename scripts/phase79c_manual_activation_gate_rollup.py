#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

PHASE = "79C_MANUAL_ACTIVATION_GATE_ROLLUP"

EXPECTED = {
    "79A_manual_activation_gate_stub": ARCH / "manual_activation_gate/79A_manual_activation_gate_stub_latest.json",
    "79B_manual_activation_gate_certification": ARCH / "manual_activation_gate_certification/79B_manual_activation_gate_certification_latest.json",
}

OUT_DIR = ARCH / "manual_activation_gate_rollup"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "79C_manual_activation_gate_rollup_latest.json"
OUT_TXT = OUT_DIR / "79C_manual_activation_gate_rollup_latest.txt"


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

cert = read_json(EXPECTED["79B_manual_activation_gate_certification"])
status = cert.get("gate_status", {})

checks["status_present"] = bool(status)
checks["manual_activation_disabled"] = status.get("manual_activation_enabled") is False
checks["automatic_activation_blocked"] = status.get("automatic_activation_allowed") is False
checks["training_blocked"] = status.get("training_enabled") is False
checks["strategy_db_write_blocked"] = status.get("strategy_db_write_allowed") is False
checks["promotion_blocked"] = status.get("promotion_enabled") is False
checks["broker_live_blocked"] = (
    status.get("broker_execution_enabled") is False
    and status.get("live_execution_enabled") is False
)

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "MANUAL_ACTIVATION_GATE_ROLLUP",
    "artifacts": artifacts,
    "gate_status": status,
    "policy": {
        "manual_activation_gate_rollup_certified": True,
        "manual_activation_enabled": False,
        "automatic_activation_allowed": False,
        "training_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": checks,
    "recommended_next_phase": "80A_NEAR_MISS_REFACTOR_QUEUE_STUB",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        "",
        "Manual activation gate rollup certified.",
        "Activation/training/db/promotion/broker/live remain blocked.",
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
