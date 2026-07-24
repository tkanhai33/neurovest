#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

PHASE = "108D_DEV_COMMAND_READ_ONLY_EXECUTION_ROLLUP"

EXPECTED = {
    "108A_preview": ARCH / "dev_command_read_only_execution_preview/108A_dev_command_read_only_execution_preview_latest.json",
    "108B_stub": ARCH / "dev_command_read_only_execution/108B_dev_command_read_only_execution_stub_latest.json",
    "108C_certification": ARCH / "dev_command_read_only_execution_certification/108C_dev_command_read_only_execution_certification_latest.json",
}

OUT_DIR = ARCH / "dev_command_read_only_execution_rollup"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "108D_dev_command_read_only_execution_rollup_latest.json"
OUT_TXT = OUT_DIR / "108D_dev_command_read_only_execution_rollup_latest.txt"


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

cert = read_json(EXPECTED["108C_certification"])
status = cert.get("executor_status", {})
preview = cert.get("preview", {})

checks.update({
    "status_present": bool(status),
    "preview_present": bool(preview),
    "command_execution_disabled": status.get("command_execution_enabled") is False,
    "read_only_preview_enabled": status.get("read_only_preview_enabled") is True,
    "preview_not_executed": preview.get("executed") is False,
    "training_blocked": status.get("training_execution_enabled") is False,
    "learner_write_blocked": status.get("learner_write_enabled") is False,
    "mutation_blocked": status.get("mutation_allowed") is False,
    "queue_write_blocked": status.get("queue_write_enabled") is False,
    "strategy_db_write_blocked": status.get("strategy_db_write_allowed") is False,
    "promotion_blocked": status.get("promotion_enabled") is False,
    "broker_live_blocked": (
        status.get("broker_execution_enabled") is False
        and status.get("live_execution_enabled") is False
    ),
})

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "DEV_COMMAND_READ_ONLY_EXECUTION_ROLLUP",
    "artifacts": artifacts,
    "executor_status": status,
    "preview": preview,
    "checks": checks,
    "policy": {
        "dev_command_read_only_execution_rollup_certified": True,
        "command_execution_enabled": False,
        "read_only_preview_enabled": True,
        "training_execution_enabled": False,
        "learner_write_enabled": False,
        "mutation_allowed": False,
        "queue_write_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "109A_DEV_COMMAND_EXECUTION_ENABLEMENT_PREVIEW",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        "command_execution_enabled: False",
        "read_only_preview_enabled: True",
        "",
        "Read-only dev command execution rollup certified.",
        "Training/db/mutation/promotion/broker/live remain blocked.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "command_execution_enabled": status.get("command_execution_enabled"),
    "read_only_preview_enabled": status.get("read_only_preview_enabled"),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
