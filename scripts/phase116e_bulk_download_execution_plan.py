#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json
import math

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "download_universe_certification/116D_download_universe_certification_latest.json"
UNIVERSE = ROOT / "backend/app/stacks/learning_research/research_data/manifests/download_universe/download_universe_v2.json"

OUT_DIR = ARCH / "bulk_download_execution_plan"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "116E_bulk_download_execution_plan_latest.json"
OUT_TXT = OUT_DIR / "116E_bulk_download_execution_plan_latest.txt"

PHASE = "116E_BULK_DOWNLOAD_EXECUTION_PLAN"
BATCH_SIZE = 12

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

source = read_json(SOURCE)
universe = read_json(UNIVERSE)

asset_groups = universe.get("asset_groups", {})
flat = []
for group, symbols in asset_groups.items():
    for symbol in symbols:
        flat.append({
            "symbol": symbol,
            "asset_group": group,
            "provider": universe.get("provider"),
            "period": universe.get("period"),
            "interval": universe.get("interval"),
        })

batches = []
for i in range(0, len(flat), BATCH_SIZE):
    batch_symbols = flat[i:i + BATCH_SIZE]
    batches.append({
        "batch_id": f"BATCH_{len(batches)+1:03d}",
        "symbol_count": len(batch_symbols),
        "symbols": batch_symbols,
        "status": "PLANNED_ONLY",
        "downloads_executed": False,
    })

plan = {
    "plan_id": "BULK_DOWNLOAD_EXECUTION_PLAN_V1",
    "created_at": datetime.now(UTC).isoformat(),
    "source_universe": str(UNIVERSE),
    "provider": universe.get("provider"),
    "period": universe.get("period"),
    "interval": universe.get("interval"),
    "total_symbols": len(flat),
    "batch_size": BATCH_SIZE,
    "batch_count": len(batches),
    "batches": batches,
    "execution_policy": {
        "downloads_enabled": False,
        "plan_only": True,
        "resume_supported": True,
        "retry_failed_symbols": True,
        "max_retries_per_symbol": 3,
        "sleep_seconds_between_batches": 5,
        "write_mode": "FILE_REPOSITORY_ONLY",
        "database_writes_allowed": False,
        "training_execution_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "output_policy": {
        "raw_ohlcv_csv": True,
        "dataset_manifest_per_symbol": True,
        "download_summary_json": True,
        "failed_symbols_json": True,
        "checksum_sha256_required": True,
    }
}

PLAN_PATH = ROOT / "backend/app/stacks/learning_research/research_data/manifests/download_universe/bulk_download_execution_plan_v1.json"
PLAN_PATH.write_text(json.dumps(plan, indent=2), encoding="utf-8")

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "universe_exists": UNIVERSE.exists(),
    "plan_written": PLAN_PATH.exists(),
    "total_symbols_144": len(flat) == 144,
    "batch_count_valid": len(batches) == math.ceil(len(flat) / BATCH_SIZE),
    "downloads_disabled": plan["execution_policy"]["downloads_enabled"] is False,
    "plan_only": plan["execution_policy"]["plan_only"] is True,
    "db_write_blocked": plan["execution_policy"]["database_writes_allowed"] is False,
    "training_blocked": plan["execution_policy"]["training_execution_enabled"] is False,
    "broker_live_blocked": (
        plan["execution_policy"]["broker_execution_enabled"] is False
        and plan["execution_policy"]["live_execution_enabled"] is False
    ),
    "checksum_required": plan["output_policy"]["checksum_sha256_required"] is True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "plan_path": str(PLAN_PATH),
    "plan": plan,
    "checks": checks,
    "policy": plan["execution_policy"],
    "recommended_next_phase": "117A_BULK_HISTORICAL_DATA_DOWNLOADER_STUB",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"total_symbols: {len(flat)}",
        f"batch_size: {BATCH_SIZE}",
        f"batch_count: {len(batches)}",
        "downloads_enabled: False",
        "",
        "Bulk download execution plan created.",
        "No downloads executed.",
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
    "total_symbols": len(flat),
    "batch_count": len(batches),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
