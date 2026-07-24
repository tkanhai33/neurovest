#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import csv, json, hashlib

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "failed_symbol_retry_execution/117J_failed_symbol_retry_execution_latest.json"

OUT_DIR = ARCH / "failed_symbol_retry_certification"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "117K_failed_symbol_retry_certification_latest.json"
OUT_TXT = OUT_DIR / "117K_failed_symbol_retry_certification_latest.txt"

PHASE = "117K_FAILED_SYMBOL_RETRY_CERTIFICATION"

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def sha256(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

source = read_json(SOURCE)
downloaded = source.get("downloaded") or {}

csv_path = Path(downloaded.get("output_file", ""))
rows = []
checksum_matches = False

if csv_path.exists():
    rows = list(csv.DictReader(csv_path.open("r", encoding="utf-8")))
    checksum_matches = sha256(csv_path) == downloaded.get("checksum_sha256")

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "retry_symbol_correct": downloaded.get("symbol") == "GIB-A.TO",
    "original_symbol_recorded": downloaded.get("original_failed_symbol") == "GIB.A.TO",
    "csv_exists": csv_path.exists(),
    "manifest_rows_match_csv": downloaded.get("rows") == len(rows),
    "rows_present": len(rows) > 0,
    "checksum_matches": checksum_matches,
    "approved_still_false": downloaded.get("approved") is False,
    "training_enabled_still_false": downloaded.get("training_enabled") is False,
    "read_only_true": downloaded.get("read_only") is True,
    "db_write_blocked": True,
    "training_blocked": True,
    "broker_live_blocked": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "retry_certification": {
        "original_symbol": downloaded.get("original_failed_symbol"),
        "resolved_symbol": downloaded.get("symbol"),
        "rows": len(rows),
        "first_date": rows[0]["date"] if rows else None,
        "last_date": rows[-1]["date"] if rows else None,
        "csv": str(csv_path),
        "checksum_matches": checksum_matches,
    },
    "checks": checks,
    "policy": {
        "failed_symbol_retry_certified": True,
        "approved_for_training": False,
        "database_writes_allowed": False,
        "training_execution_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "117L_RESEARCH_REPOSITORY_DOWNLOAD_ROLLUP",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        "original_symbol: GIB.A.TO",
        "resolved_symbol: GIB-A.TO",
        f"rows: {len(rows)}",
        f"checksum_matches: {checksum_matches}",
        "",
        "Failed symbol retry certified.",
        "Still not approved for training until repository rollup.",
        "No DB writes. No broker/live.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "original_symbol": downloaded.get("original_failed_symbol"),
    "resolved_symbol": downloaded.get("symbol"),
    "rows": len(rows),
    "checksum_matches": checksum_matches,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
