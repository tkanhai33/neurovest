#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import csv, json, hashlib

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "failed_symbol_retry_preview/117I_failed_symbol_retry_preview_latest.json"
RESEARCH_ROOT = ROOT / "backend/app/stacks/learning_research/research_data"

OUT_DIR = ARCH / "failed_symbol_retry_execution"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "117J_failed_symbol_retry_execution_latest.json"
OUT_TXT = OUT_DIR / "117J_failed_symbol_retry_execution_latest.txt"

PHASE = "117J_FAILED_SYMBOL_RETRY_EXECUTION"

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def sha256(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def scalar(v):
    try:
        if hasattr(v, "iloc"):
            return v.iloc[0]
    except Exception:
        pass
    return v

source = read_json(SOURCE)
preview = source.get("retry_preview", {})

original_symbol = preview.get("original_symbol")
retry_symbol = preview.get("retry_symbol")
asset_group = preview.get("asset_group", "equities_canada")

safe_symbol = retry_symbol.replace("^", "").replace(".", "_").replace("=", "_").replace("-", "_")

raw_dir = RESEARCH_ROOT / asset_group / "raw"
meta_dir = RESEARCH_ROOT / asset_group / "metadata"
raw_dir.mkdir(parents=True, exist_ok=True)
meta_dir.mkdir(parents=True, exist_ok=True)

out_csv = raw_dir / f"{safe_symbol}.csv"
out_manifest = meta_dir / f"{safe_symbol}_manifest.json"

downloaded = None
failed = None

try:
    import yfinance as yf

    data = yf.download(
        retry_symbol,
        period="max",
        interval="1d",
        auto_adjust=False,
        progress=False,
        threads=False,
    )

    rows = []
    for idx, row in data.iterrows():
        rows.append({
            "symbol": retry_symbol,
            "original_failed_symbol": original_symbol,
            "date": str(idx.date()),
            "open": float(scalar(row["Open"])),
            "high": float(scalar(row["High"])),
            "low": float(scalar(row["Low"])),
            "close": float(scalar(row["Close"])),
            "adj_close": float(scalar(row["Adj Close"])) if "Adj Close" in row else None,
            "volume": int(scalar(row["Volume"])),
        })

    if not rows:
        raise RuntimeError("no rows returned")

    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "symbol", "original_failed_symbol", "date", "open", "high", "low",
            "close", "adj_close", "volume"
        ])
        writer.writeheader()
        writer.writerows(rows)

    digest = sha256(out_csv)

    downloaded = {
        "dataset_id": f"YFINANCE_{asset_group.upper()}_{safe_symbol}",
        "provider": "YFINANCE",
        "asset_group": asset_group,
        "original_failed_symbol": original_symbol,
        "symbol": retry_symbol,
        "period": "max",
        "interval": "1d",
        "output_file": str(out_csv),
        "checksum_sha256": digest,
        "rows": len(rows),
        "first_date": rows[0]["date"],
        "last_date": rows[-1]["date"],
        "approved": False,
        "read_only": True,
        "normalized": False,
        "training_enabled": False,
        "created_at": datetime.now(UTC).isoformat(),
        "updated_at": datetime.now(UTC).isoformat(),
    }

    out_manifest.write_text(json.dumps(downloaded, indent=2), encoding="utf-8")

except Exception as exc:
    failed = {
        "original_failed_symbol": original_symbol,
        "retry_symbol": retry_symbol,
        "asset_group": asset_group,
        "error": str(exc),
    }

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "retry_symbol_present": retry_symbol == "GIB-A.TO",
    "download_succeeded": downloaded is not None,
    "manifest_written": out_manifest.exists(),
    "csv_written": out_csv.exists(),
    "rows_present": downloaded is not None and downloaded.get("rows", 0) > 0,
    "checksum_present": downloaded is not None and bool(downloaded.get("checksum_sha256")),
    "db_write_blocked": True,
    "training_blocked": True,
    "broker_live_blocked": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "downloaded": downloaded,
    "failed": failed,
    "checks": checks,
    "policy": {
        "file_repository_writes_executed": downloaded is not None,
        "database_writes_allowed": False,
        "training_execution_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "117K_FAILED_SYMBOL_RETRY_CERTIFICATION",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"original_symbol: {original_symbol}",
        f"retry_symbol: {retry_symbol}",
        f"rows: {downloaded.get('rows') if downloaded else 0}",
        f"failed: {failed is not None}",
        "",
        "Failed symbol retry execution completed.",
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
    "original_symbol": original_symbol,
    "retry_symbol": retry_symbol,
    "rows": downloaded.get("rows") if downloaded else 0,
    "failed": failed,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
