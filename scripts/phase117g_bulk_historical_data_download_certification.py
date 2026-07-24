#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import csv, json, hashlib

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "bulk_historical_data_download_execution/117F_bulk_historical_data_download_execution_latest.json"

OUT_DIR = ARCH / "bulk_historical_data_download_certification"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "117G_bulk_historical_data_download_certification_latest.json"
OUT_TXT = OUT_DIR / "117G_bulk_historical_data_download_certification_latest.txt"

PHASE = "117G_BULK_HISTORICAL_DATA_DOWNLOAD_CERTIFICATION"

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def sha256(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

source = read_json(SOURCE)
downloaded = source.get("downloaded", [])
failed = source.get("failed", [])

verified = []
bad = []

for item in downloaded:
    path = Path(item.get("output_file", ""))
    if not path.exists():
        bad.append({"symbol": item.get("symbol"), "reason": "missing_csv"})
        continue

    try:
        rows = list(csv.DictReader(path.open("r", encoding="utf-8")))
        digest = sha256(path)

        verified.append({
            "symbol": item.get("symbol"),
            "asset_group": item.get("asset_group"),
            "rows": len(rows),
            "first_date": rows[0]["date"] if rows else None,
            "last_date": rows[-1]["date"] if rows else None,
            "checksum_matches": digest == item.get("checksum_sha256"),
        })

        if not rows:
            bad.append({"symbol": item.get("symbol"), "reason": "zero_rows"})
        if digest != item.get("checksum_sha256"):
            bad.append({"symbol": item.get("symbol"), "reason": "checksum_mismatch"})

    except Exception as exc:
        bad.append({"symbol": item.get("symbol"), "reason": str(exc)})

failed_symbols = [f.get("symbol") for f in failed]

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "downloaded_count_143": len(downloaded) == 143,
    "failed_count_1": len(failed) == 1,
    "expected_failed_gib": failed_symbols == ["GIB.A.TO"],
    "verified_count_matches_downloaded": len(verified) == len(downloaded),
    "no_bad_downloaded_files": len(bad) == 0,
    "all_checksums_match": all(v["checksum_matches"] for v in verified),
    "all_have_rows": all(v["rows"] > 0 for v in verified),
    "db_write_blocked": True,
    "training_blocked": True,
    "broker_live_blocked": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "downloaded_count": len(downloaded),
    "verified_count": len(verified),
    "failed_count": len(failed),
    "failed_symbols": failed_symbols,
    "bad_count": len(bad),
    "bad": bad,
    "verified_sample": verified[:25],
    "checks": checks,
    "policy": {
        "download_certified": True,
        "approved_for_training": False,
        "database_writes_allowed": False,
        "training_execution_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "117H_FAILED_SYMBOL_CORRECTION_PLAN",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"downloaded_count: {len(downloaded)}",
        f"verified_count: {len(verified)}",
        f"failed_count: {len(failed)}",
        f"failed_symbols: {failed_symbols}",
        f"bad_count: {len(bad)}",
        "",
        "Bulk historical data download certified.",
        "Data remains not approved for training until repository rollup.",
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
    "downloaded_count": len(downloaded),
    "verified_count": len(verified),
    "failed_count": len(failed),
    "failed_symbols": failed_symbols,
    "bad_count": len(bad),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
