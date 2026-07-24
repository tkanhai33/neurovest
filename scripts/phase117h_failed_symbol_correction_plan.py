#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "bulk_historical_data_download_certification/117G_bulk_historical_data_download_certification_latest.json"

OUT_DIR = ARCH / "failed_symbol_correction_plan"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "117H_failed_symbol_correction_plan_latest.json"
OUT_TXT = OUT_DIR / "117H_failed_symbol_correction_plan_latest.txt"

PHASE = "117H_FAILED_SYMBOL_CORRECTION_PLAN"

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

source = read_json(SOURCE)
failed_symbols = source.get("failed_symbols", [])

correction_plan = {
    "failed_symbols": failed_symbols,
    "corrections": [
        {
            "original_symbol": "GIB.A.TO",
            "suspected_issue": "Yahoo Finance does not recognize dot-class TSX ticker format",
            "candidate_replacements": ["GIB-A.TO", "GIB.TO"],
            "recommended_first_retry": "GIB-A.TO",
            "action": "RETRY_WITH_ALTERNATE_SYMBOL",
            "auto_apply_allowed": False,
        }
    ],
    "policy": {
        "plan_only": True,
        "downloads_executed": False,
        "manifest_modified": False,
        "database_writes_allowed": False,
        "training_execution_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
}

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "failed_symbol_present": failed_symbols == ["GIB.A.TO"],
    "correction_present": len(correction_plan["corrections"]) == 1,
    "candidate_replacement_present": "GIB-A.TO" in correction_plan["corrections"][0]["candidate_replacements"],
    "plan_only": correction_plan["policy"]["plan_only"] is True,
    "downloads_not_executed": correction_plan["policy"]["downloads_executed"] is False,
    "manifest_not_modified": correction_plan["policy"]["manifest_modified"] is False,
    "db_write_blocked": correction_plan["policy"]["database_writes_allowed"] is False,
    "training_blocked": correction_plan["policy"]["training_execution_enabled"] is False,
    "broker_live_blocked": (
        correction_plan["policy"]["broker_execution_enabled"] is False
        and correction_plan["policy"]["live_execution_enabled"] is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "correction_plan": correction_plan,
    "checks": checks,
    "recommended_next_phase": "117I_FAILED_SYMBOL_RETRY_PREVIEW",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"failed_symbols: {failed_symbols}",
        "recommended_retry: GIB-A.TO",
        "downloads_executed: False",
        "",
        "Failed symbol correction plan created.",
        "No manifest modification. No DB writes. No training. No broker/live.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "failed_symbols": failed_symbols,
    "recommended_retry": "GIB-A.TO",
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
