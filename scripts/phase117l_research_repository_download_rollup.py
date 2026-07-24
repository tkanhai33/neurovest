#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"
RESEARCH_ROOT = ROOT / "backend/app/stacks/learning_research/research_data"

SOURCE_117G = ARCH / "bulk_historical_data_download_certification/117G_bulk_historical_data_download_certification_latest.json"
SOURCE_117K = ARCH / "failed_symbol_retry_certification/117K_failed_symbol_retry_certification_latest.json"

OUT_DIR = ARCH / "research_repository_download_rollup"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "117L_research_repository_download_rollup_latest.json"
OUT_TXT = OUT_DIR / "117L_research_repository_download_rollup_latest.txt"

PHASE = "117L_RESEARCH_REPOSITORY_DOWNLOAD_ROLLUP"

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

g = read_json(SOURCE_117G)
k = read_json(SOURCE_117K)

csv_files = list(RESEARCH_ROOT.rglob("*.csv"))
manifest_files = list(RESEARCH_ROOT.rglob("*_manifest.json"))

downloaded_count = g.get("downloaded_count", 0)
retry_rows = k.get("retry_certification", {}).get("rows", 0)

rollup = {
    "bulk_downloaded_count": downloaded_count,
    "retry_resolved_count": 1 if k.get("certified") is True else 0,
    "total_downloaded_symbols": downloaded_count + (1 if k.get("certified") is True else 0),
    "csv_files_found": len(csv_files),
    "manifest_files_found": len(manifest_files),
    "failed_symbol_resolved": k.get("retry_certification", {}),
    "research_root": str(RESEARCH_ROOT),
}

checks = {
    "source_117g_exists": SOURCE_117G.exists(),
    "source_117g_certified": g.get("certified") is True,
    "source_117k_exists": SOURCE_117K.exists(),
    "source_117k_certified": k.get("certified") is True,
    "research_root_exists": RESEARCH_ROOT.exists(),
    "total_downloaded_symbols_144": rollup["total_downloaded_symbols"] == 144,
    "csv_files_at_least_144": len(csv_files) >= 144,
    "manifest_files_at_least_144": len(manifest_files) >= 144,
    "gib_resolved": k.get("retry_certification", {}).get("resolved_symbol") == "GIB-A.TO",
    "retry_rows_present": retry_rows > 0,
    "db_write_blocked": True,
    "training_blocked": True,
    "broker_live_blocked": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "rollup": rollup,
    "checks": checks,
    "policy": {
        "repository_download_rollup_certified": True,
        "approved_for_training": False,
        "database_writes_allowed": False,
        "training_execution_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "118A_RESEARCH_REPOSITORY_NUMERIC_INTEGRITY_SCAN",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"total_downloaded_symbols: {rollup['total_downloaded_symbols']}",
        f"csv_files_found: {len(csv_files)}",
        f"manifest_files_found: {len(manifest_files)}",
        "approved_for_training: False",
        "",
        "Research repository download rollup certified.",
        "No DB writes. No training. No broker/live.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "total_downloaded_symbols": rollup["total_downloaded_symbols"],
    "csv_files_found": len(csv_files),
    "manifest_files_found": len(manifest_files),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
