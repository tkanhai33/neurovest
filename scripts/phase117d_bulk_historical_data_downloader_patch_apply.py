#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json
import py_compile

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "bulk_historical_data_downloader_enablement_preview/117C_bulk_historical_data_downloader_enablement_preview_latest.json"
TARGET = ROOT / "backend/app/stacks/learning_research/L3_service_facade/bulk_historical_data_downloader.py"

OUT_DIR = ARCH / "bulk_historical_data_downloader_patch_apply"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "117D_bulk_historical_data_downloader_patch_apply_latest.json"
OUT_TXT = OUT_DIR / "117D_bulk_historical_data_downloader_patch_apply_latest.txt"

PHASE = "117D_BULK_HISTORICAL_DATA_DOWNLOADER_PATCH_APPLY"

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

source = read_json(SOURCE)

text_before = TARGET.read_text(encoding="utf-8")

text_after = text_before.replace(
    "DOWNLOADS_ENABLED = False",
    "DOWNLOADS_ENABLED = True",
    1,
).replace(
    "FILE_REPOSITORY_WRITES_ENABLED = False",
    "FILE_REPOSITORY_WRITES_ENABLED = True",
    1,
)

TARGET.write_text(text_after, encoding="utf-8")

compile_ok = False
compile_error = None

try:
    py_compile.compile(str(TARGET), doraise=True)
    compile_ok = True
except Exception as exc:
    compile_error = {"type": type(exc).__name__, "message": str(exc)}

text = TARGET.read_text(encoding="utf-8")

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "target_exists": TARGET.exists(),
    "compile_ok": compile_ok,
    "downloads_enabled": "DOWNLOADS_ENABLED = True" in text,
    "file_repository_writes_enabled": "FILE_REPOSITORY_WRITES_ENABLED = True" in text,
    "database_writes_still_blocked": "DATABASE_WRITES_ALLOWED = False" in text,
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
    "target_file": str(TARGET),
    "compile_error": compile_error,
    "checks": checks,
    "policy": {
        "downloads_enabled": True,
        "file_repository_writes_enabled": True,
        "database_writes_allowed": False,
        "training_execution_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "117E_BULK_HISTORICAL_DATA_DOWNLOADER_ENABLEMENT_CERTIFICATION",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"compile_ok: {compile_ok}",
        "downloads_enabled: True",
        "file_repository_writes_enabled: True",
        "database_writes_allowed: False",
        "training_execution_enabled: False",
        "",
        "Downloader enabled for file-repository historical data downloads only.",
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
    "compile_ok": compile_ok,
    "downloads_enabled": True,
    "file_repository_writes_enabled": True,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
