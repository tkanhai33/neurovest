#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import importlib.util
import json
import py_compile

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "bulk_historical_data_downloader_stub/117A_bulk_historical_data_downloader_stub_latest.json"
PLAN = ROOT / "backend/app/stacks/learning_research/research_data/manifests/download_universe/bulk_download_execution_plan_v1.json"
TARGET = ROOT / "backend/app/stacks/learning_research/L3_service_facade/bulk_historical_data_downloader.py"

OUT_DIR = ARCH / "bulk_historical_data_downloader_certification"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "117B_bulk_historical_data_downloader_certification_latest.json"
OUT_TXT = OUT_DIR / "117B_bulk_historical_data_downloader_certification_latest.txt"

PHASE = "117B_BULK_HISTORICAL_DATA_DOWNLOADER_CERTIFICATION"

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def import_file(path: Path):
    spec = importlib.util.spec_from_file_location("bulk_historical_data_downloader", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

source = read_json(SOURCE)
errors = []
compile_ok = False
status = {}
preview = {}
sample_manifest = {}

try:
    py_compile.compile(str(TARGET), doraise=True)
    compile_ok = True
except Exception as exc:
    errors.append({"type": type(exc).__name__, "message": str(exc)})

try:
    module = import_file(TARGET)
    status = module.downloader_status()
    plan = module.load_bulk_download_plan(PLAN)
    preview = module.preview_download_batches(plan)
    sample_manifest = module.build_symbol_dataset_manifest(
        symbol="SHOP.TO",
        asset_group="equities_canada",
        provider="YFINANCE",
        interval="1d",
        period="max",
        output_file="preview_only.csv",
    )
except Exception as exc:
    errors.append({"type": type(exc).__name__, "message": str(exc)})

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "plan_exists": PLAN.exists(),
    "target_exists": TARGET.exists(),
    "compile_ok": compile_ok,
    "status_present": bool(status),
    "preview_present": bool(preview),
    "sample_manifest_present": bool(sample_manifest),
    "downloads_disabled": status.get("downloads_enabled") is False,
    "file_writes_disabled": status.get("file_repository_writes_enabled") is False,
    "db_write_blocked": status.get("database_writes_allowed") is False,
    "training_blocked": status.get("training_execution_enabled") is False,
    "strategy_db_write_blocked": status.get("strategy_db_write_allowed") is False,
    "promotion_blocked": status.get("promotion_enabled") is False,
    "broker_live_blocked": (
        status.get("broker_execution_enabled") is False
        and status.get("live_execution_enabled") is False
    ),
    "preview_no_downloads_executed": preview.get("downloads_executed") is False,
    "preview_total_symbols_144": preview.get("total_symbols") == 144,
    "sample_manifest_read_only": sample_manifest.get("read_only") is True,
    "sample_manifest_training_disabled": sample_manifest.get("training_enabled") is False,
    "sample_manifest_not_approved": sample_manifest.get("approved") is False,
    "no_errors": len(errors) == 0,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "target_file": str(TARGET),
    "plan_file": str(PLAN),
    "downloader_status": status,
    "preview": preview,
    "sample_manifest": sample_manifest,
    "errors": errors,
    "checks": checks,
    "policy": {
        "bulk_historical_data_downloader_certified": True,
        "downloads_enabled": False,
        "file_repository_writes_enabled": False,
        "database_writes_allowed": False,
        "training_execution_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "117C_BULK_HISTORICAL_DATA_DOWNLOADER_ENABLEMENT_PREVIEW",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"compile_ok: {compile_ok}",
        f"total_symbols_preview: {preview.get('total_symbols')}",
        f"errors: {len(errors)}",
        "",
        "Bulk historical downloader certified in disabled preview mode.",
        "No downloads. No file writes. No DB writes. No broker/live.",
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
    "total_symbols_preview": preview.get("total_symbols"),
    "errors": errors,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
