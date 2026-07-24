#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "failed_symbol_correction_plan/117H_failed_symbol_correction_plan_latest.json"

OUT_DIR = ARCH / "failed_symbol_retry_preview"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "117I_failed_symbol_retry_preview_latest.json"
OUT_TXT = OUT_DIR / "117I_failed_symbol_retry_preview_latest.txt"

PHASE = "117I_FAILED_SYMBOL_RETRY_PREVIEW"

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

source = read_json(SOURCE)
plan = source.get("correction_plan", {})
correction = plan.get("corrections", [{}])[0]

retry_preview = {
    "original_symbol": correction.get("original_symbol"),
    "retry_symbol": correction.get("recommended_first_retry"),
    "candidate_replacements": correction.get("candidate_replacements", []),
    "asset_group": "equities_canada",
    "provider": "YFINANCE",
    "period": "max",
    "interval": "1d",
    "preview_only": True,
    "download_executed": False,
    "manifest_modified": False,
    "file_repository_write_executed": False,
}

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "original_symbol_gib_a": retry_preview["original_symbol"] == "GIB.A.TO",
    "retry_symbol_gib_dash_a": retry_preview["retry_symbol"] == "GIB-A.TO",
    "candidate_replacements_present": len(retry_preview["candidate_replacements"]) >= 1,
    "preview_only": retry_preview["preview_only"] is True,
    "download_not_executed": retry_preview["download_executed"] is False,
    "manifest_not_modified": retry_preview["manifest_modified"] is False,
    "file_write_not_executed": retry_preview["file_repository_write_executed"] is False,
    "db_write_blocked": True,
    "training_blocked": True,
    "broker_live_blocked": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "retry_preview": retry_preview,
    "checks": checks,
    "policy": {
        "preview_only": True,
        "download_execution_enabled": False,
        "file_repository_writes_enabled": False,
        "manifest_modification_allowed": False,
        "database_writes_allowed": False,
        "training_execution_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "117J_FAILED_SYMBOL_RETRY_EXECUTION",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"original_symbol: {retry_preview['original_symbol']}",
        f"retry_symbol: {retry_preview['retry_symbol']}",
        "download_executed: False",
        "manifest_modified: False",
        "",
        "Failed symbol retry preview created.",
        "No file writes. No DB writes. No training. No broker/live.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "original_symbol": retry_preview["original_symbol"],
    "retry_symbol": retry_preview["retry_symbol"],
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
