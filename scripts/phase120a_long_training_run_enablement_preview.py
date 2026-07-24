#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "replay_validation_certification/119D_replay_validation_certification_latest.json"

OUT_DIR = ARCH / "long_training_run_enablement_preview"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "120A_long_training_run_enablement_preview_latest.json"
OUT_TXT = OUT_DIR / "120A_long_training_run_enablement_preview_latest.txt"

PHASE = "120A_LONG_TRAINING_RUN_ENABLEMENT_PREVIEW"

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

source = read_json(SOURCE)

preview = {
    "mode": "LONG_TRAINING_ENABLEMENT_PREVIEW_ONLY",
    "planned_run": {
        "duration_hours": 8,
        "duration_seconds": 28800,
        "repository_symbols": 144,
        "excluded_rows": 6,
        "checkpoint_every_seconds": 300,
        "heartbeat_every_seconds": 30,
        "resume_supported": True,
    },
    "planned_enablement": {
        "training_execution_enabled": True,
        "database_writes_allowed": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "apply_now": False,
}

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "approved_for_long_training_preview": source.get("policy", {}).get("approved_for_long_training_preview") is True,
    "duration_8_hours": preview["planned_run"]["duration_seconds"] == 28800,
    "repository_symbols_144": preview["planned_run"]["repository_symbols"] == 144,
    "excluded_rows_6": preview["planned_run"]["excluded_rows"] == 6,
    "checkpointing_present": preview["planned_run"]["checkpoint_every_seconds"] == 300,
    "resume_supported": preview["planned_run"]["resume_supported"] is True,
    "preview_only": preview["apply_now"] is False,
    "db_write_blocked": preview["planned_enablement"]["database_writes_allowed"] is False,
    "broker_live_blocked": (
        preview["planned_enablement"]["broker_execution_enabled"] is False
        and preview["planned_enablement"]["live_execution_enabled"] is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "preview": preview,
    "checks": checks,
    "policy": {
        "preview_only": True,
        "training_execution_enabled_now": False,
        "training_execution_enabled_after_patch": True,
        "database_writes_allowed": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "120B_LONG_TRAINING_RUN_EXECUTOR_STUB",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        "preview_only: True",
        "planned_duration_hours: 8",
        "repository_symbols: 144",
        "excluded_rows: 6",
        "training_enabled_now: False",
        "training_enabled_after_patch: True",
        "DB/broker/live remain blocked.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "planned_duration_hours": 8,
    "repository_symbols": 144,
    "excluded_rows": 6,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
