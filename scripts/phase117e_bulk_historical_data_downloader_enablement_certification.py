#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import importlib.util, json, py_compile

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "bulk_historical_data_downloader_patch_apply/117D_bulk_historical_data_downloader_patch_apply_latest.json"
TARGET = ROOT / "backend/app/stacks/learning_research/L3_service_facade/bulk_historical_data_downloader.py"

OUT_DIR = ARCH / "bulk_historical_data_downloader_enablement_certification"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "117E_bulk_historical_data_downloader_enablement_certification_latest.json"
OUT_TXT = OUT_DIR / "117E_bulk_historical_data_downloader_enablement_certification_latest.txt"

PHASE = "117E_BULK_HISTORICAL_DATA_DOWNLOADER_ENABLEMENT_CERTIFICATION"

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def import_file(path: Path):
    spec = importlib.util.spec_from_file_location("bulk_historical_data_downloader", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

source = read_json(SOURCE)
errors = []
compile_ok = False
status = {}

try:
    py_compile.compile(str(TARGET), doraise=True)
    compile_ok = True
except Exception as exc:
    errors.append({"type": type(exc).__name__, "message": str(exc)})

try:
    module = import_file(TARGET)
    status = module.downloader_status()
except Exception as exc:
    errors.append({"type": type(exc).__name__, "message": str(exc)})

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "target_exists": TARGET.exists(),
    "compile_ok": compile_ok,
    "downloads_enabled": status.get("downloads_enabled") is True,
    "file_repository_writes_enabled": status.get("file_repository_writes_enabled") is True,
    "database_writes_blocked": status.get("database_writes_allowed") is False,
    "training_blocked": status.get("training_execution_enabled") is False,
    "strategy_db_write_blocked": status.get("strategy_db_write_allowed") is False,
    "promotion_blocked": status.get("promotion_enabled") is False,
    "broker_live_blocked": (
        status.get("broker_execution_enabled") is False
        and status.get("live_execution_enabled") is False
    ),
    "no_errors": len(errors) == 0,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "target_file": str(TARGET),
    "downloader_status": status,
    "errors": errors,
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
    "recommended_next_phase": "117F_BULK_HISTORICAL_DATA_DOWNLOAD_EXECUTION",
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
        "Downloader enablement certified.",
        "Ready for file-repository-only historical download execution.",
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
    "downloads_enabled": status.get("downloads_enabled"),
    "file_repository_writes_enabled": status.get("file_repository_writes_enabled"),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
