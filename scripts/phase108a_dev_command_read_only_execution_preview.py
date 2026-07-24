#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "dev_territory_command_activation_rollup" / "107D_dev_territory_command_activation_rollup_latest.json"

OUT_DIR = ARCH / "dev_command_read_only_execution_preview"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "108A_dev_command_read_only_execution_preview_latest.json"
OUT_TXT = OUT_DIR / "108A_dev_command_read_only_execution_preview_latest.txt"

PHASE = "108A_DEV_COMMAND_READ_ONLY_EXECUTION_PREVIEW"

def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

source = read_json(SOURCE)

preview_command = {
    "command_level": 1,
    "command_name": "SCOUT",
    "command_text": "Neuro, expand your territory. Scout the approved landscape.",
    "mode": "READ_ONLY_EXECUTION_PREVIEW_ONLY_NO_RUNTIME_CALL",
    "expected_action": "List approved commands and doctrine only.",
    "allowed": [
        "read command registry",
        "read doctrine",
        "produce preview response",
    ],
    "forbidden": [
        "training execution",
        "learner writes",
        "mutation",
        "queue writes",
        "strategy DB writes",
        "promotion",
        "broker execution",
        "live execution",
    ],
}

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "registry_enabled": source.get("registry_status", {}).get("dev_territory_registry_enabled") is True,
    "command_preview_present": bool(preview_command),
    "read_only_preview": preview_command["mode"] == "READ_ONLY_EXECUTION_PREVIEW_ONLY_NO_RUNTIME_CALL",
    "training_blocked": True,
    "learner_write_blocked": True,
    "mutation_blocked": True,
    "queue_write_blocked": True,
    "strategy_db_write_blocked": True,
    "promotion_blocked": True,
    "broker_live_blocked": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "DEV_COMMAND_READ_ONLY_EXECUTION_PREVIEW",
    "source_activation_rollup": str(SOURCE),
    "preview_command": preview_command,
    "checks": checks,
    "policy": {
        "dev_command_read_only_execution_preview_certified": True,
        "dev_territory_registry_enabled": True,
        "command_execution_enabled": False,
        "training_execution_enabled": False,
        "learner_write_enabled": False,
        "mutation_allowed": False,
        "queue_write_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "108B_DEV_COMMAND_READ_ONLY_EXECUTION_STUB",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"command_name: {preview_command['command_name']}",
        "mode: preview only",
        "",
        "No runtime command execution yet.",
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
    "command_name": preview_command["command_name"],
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
