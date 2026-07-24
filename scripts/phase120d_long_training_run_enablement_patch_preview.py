#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "long_training_run_executor_certification/120C_long_training_run_executor_certification_latest.json"
TARGET = ROOT / "backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/long_training_run_executor.py"

OUT_DIR = ARCH / "long_training_run_enablement_patch_preview"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "120D_long_training_run_enablement_patch_preview_latest.json"
OUT_TXT = OUT_DIR / "120D_long_training_run_enablement_patch_preview_latest.txt"

PHASE = "120D_LONG_TRAINING_RUN_ENABLEMENT_PATCH_PREVIEW"

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

source = read_json(SOURCE)
text = TARGET.read_text(encoding="utf-8") if TARGET.exists() else ""

preview = {
    "mode": "PATCH_PREVIEW_ONLY_NO_APPLY",
    "target_file": str(TARGET),
    "planned_change": {
        "from": "TRAINING_EXECUTION_ENABLED = False",
        "to": "TRAINING_EXECUTION_ENABLED = True",
    },
    "still_blocked": {
        "DATABASE_WRITES_ALLOWED": False,
        "STRATEGY_DB_WRITE_ALLOWED": False,
        "PROMOTION_ENABLED": False,
        "BROKER_EXECUTION_ENABLED": False,
        "LIVE_EXECUTION_ENABLED": False,
    },
    "planned_run_contract": {
        "duration_seconds": 28800,
        "heartbeat_seconds": 30,
        "checkpoint_seconds": 300,
        "repository_symbols": 144,
        "excluded_rows": 6,
    },
}

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "target_exists": TARGET.exists(),
    "training_currently_disabled": "TRAINING_EXECUTION_ENABLED = False" in text,
    "duration_8h_present": "DEFAULT_DURATION_SECONDS = 28800" in text,
    "heartbeat_30s_present": "DEFAULT_HEARTBEAT_SECONDS = 30" in text,
    "checkpoint_300s_present": "DEFAULT_CHECKPOINT_SECONDS = 300" in text,
    "preview_only_no_apply": preview["mode"] == "PATCH_PREVIEW_ONLY_NO_APPLY",
    "db_write_still_blocked": "DATABASE_WRITES_ALLOWED = False" in text,
    "strategy_db_write_still_blocked": "STRATEGY_DB_WRITE_ALLOWED = False" in text,
    "promotion_still_blocked": "PROMOTION_ENABLED = False" in text,
    "broker_live_still_blocked": (
        "BROKER_EXECUTION_ENABLED = False" in text
        and "LIVE_EXECUTION_ENABLED = False" in text
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "preview": preview,
    "checks": checks,
    "policy": {
        "patch_apply_allowed_now": False,
        "training_execution_enabled_now": False,
        "training_execution_enabled_after_patch": True,
        "database_writes_allowed": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "120E_LONG_TRAINING_RUN_ENABLEMENT_PATCH_APPLY",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        "patch_apply_allowed_now: False",
        "planned: TRAINING_EXECUTION_ENABLED False -> True",
        "DB/strategy DB/promotion/broker/live remain blocked.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "patch_apply_allowed_now": False,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
