#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "bulk_historical_data_downloader_certification/117B_bulk_historical_data_downloader_certification_latest.json"
TARGET = ROOT / "backend/app/stacks/learning_research/L3_service_facade/bulk_historical_data_downloader.py"

OUT_DIR = ARCH / "bulk_historical_data_downloader_enablement_preview"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "117C_bulk_historical_data_downloader_enablement_preview_latest.json"
OUT_TXT = OUT_DIR / "117C_bulk_historical_data_downloader_enablement_preview_latest.txt"

PHASE = "117C_BULK_HISTORICAL_DATA_DOWNLOADER_ENABLEMENT_PREVIEW"

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

source = read_json(SOURCE)
text = TARGET.read_text(encoding="utf-8") if TARGET.exists() else ""

preview = {
    "mode": "ENABLEMENT_PREVIEW_ONLY_NO_PATCH",
    "target_file": str(TARGET),
    "planned_changes": {
        "DOWNLOADS_ENABLED": {"from": False, "to": True},
        "FILE_REPOSITORY_WRITES_ENABLED": {"from": False, "to": True},
    },
    "still_blocked": {
        "DATABASE_WRITES_ALLOWED": False,
        "TRAINING_EXECUTION_ENABLED": False,
        "STRATEGY_DB_WRITE_ALLOWED": False,
        "PROMOTION_ENABLED": False,
        "BROKER_EXECUTION_ENABLED": False,
        "LIVE_EXECUTION_ENABLED": False,
    },
}

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "target_exists": TARGET.exists(),
    "downloads_currently_disabled": "DOWNLOADS_ENABLED = False" in text,
    "file_writes_currently_disabled": "FILE_REPOSITORY_WRITES_ENABLED = False" in text,
    "preview_only_no_patch": preview["mode"] == "ENABLEMENT_PREVIEW_ONLY_NO_PATCH",
    "db_write_still_blocked": "DATABASE_WRITES_ALLOWED = False" in text,
    "training_still_blocked": "TRAINING_EXECUTION_ENABLED = False" in text,
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
        "downloads_enabled": False,
        "file_repository_writes_enabled": False,
        "database_writes_allowed": False,
        "training_execution_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "117D_BULK_HISTORICAL_DATA_DOWNLOADER_PATCH_APPLY",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        "preview_only: True",
        "planned: downloads False -> True",
        "planned: file repository writes False -> True",
        "DB/training/promotion/broker/live remain blocked.",
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
