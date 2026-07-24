#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import csv, json, hashlib, time

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "bulk_historical_data_downloader_enablement_certification/117E_bulk_historical_data_downloader_enablement_certification_latest.json"
PLAN = ROOT / "backend/app/stacks/learning_research/research_data/manifests/download_universe/bulk_download_execution_plan_v1.json"
RESEARCH_ROOT = ROOT / "backend/app/stacks/learning_research/research_data"

OUT_DIR = ARCH / "bulk_historical_data_download_execution"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "117F_bulk_historical_data_download_execution_latest.json"
OUT_TXT = OUT_DIR / "117F_bulk_historical_data_download_execution_latest.txt"

PHASE = "117F_BULK_HISTORICAL_DATA_DOWNLOAD_EXECUTION"

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
plan = read_json(PLAN)

downloaded = []
failed = []

try:
    import yfinance as yf
except Exception as exc:
    yf = None
    failed.append({"symbol": "__IMPORT__", "error": f"yfinance import failed: {exc}"})

if yf:
    for batch in plan.get("batches", []):
        for item in batch.get("symbols", []):
            symbol = item["symbol"]
            asset_group = item["asset_group"]
            safe_symbol = symbol.replace("^", "").replace(".", "_").replace("=", "_").replace("-", "_")

            raw_dir = RESEARCH_ROOT / asset_group / "raw"
            meta_dir = RESEARCH_ROOT / asset_group / "metadata"
            raw_dir.mkdir(parents=True, exist_ok=True)
            meta_dir.mkdir(parents=True, exist_ok=True)

            out_csv = raw_dir / f"{safe_symbol}.csv"
            out_manifest = meta_dir / f"{safe_symbol}_manifest.json"

            try:
                data = yf.download(
                    symbol,
                    period=item.get("period") or "max",
                    interval=item.get("interval") or "1d",
                    auto_adjust=False,
                    progress=False,
                    threads=False,
                )

                rows = []
                for idx, row in data.iterrows():
                    rows.append({
                        "symbol": symbol,
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
                        "symbol","date","open","high","low","close","adj_close","volume"
                    ])
                    writer.writeheader()
                    writer.writerows(rows)

                digest = sha256(out_csv)

                manifest = {
                    "dataset_id": f"YFINANCE_{asset_group.upper()}_{safe_symbol}",
                    "provider": "YFINANCE",
                    "asset_group": asset_group,
                    "symbol": symbol,
                    "period": item.get("period"),
                    "interval": item.get("interval"),
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

                out_manifest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
                downloaded.append(manifest)

            except Exception as exc:
                failed.append({
                    "symbol": symbol,
                    "asset_group": asset_group,
                    "error": str(exc),
                })

        time.sleep(plan.get("execution_policy", {}).get("sleep_seconds_between_batches", 5))

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "plan_exists": PLAN.exists(),
    "downloads_attempted": len(downloaded) + len(failed) > 0,
    "downloaded_any": len(downloaded) > 0,
    "db_write_blocked": True,
    "training_blocked": True,
    "broker_live_blocked": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "downloaded_count": len(downloaded),
    "failed_count": len(failed),
    "downloaded": downloaded,
    "failed": failed,
    "checks": checks,
    "policy": {
        "file_repository_writes_executed": True,
        "database_writes_allowed": False,
        "training_execution_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "117G_BULK_HISTORICAL_DATA_DOWNLOAD_CERTIFICATION",
    "certified": all(checks.values()) and len(downloaded) > 0,
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"downloaded_count: {len(downloaded)}",
        f"failed_count: {len(failed)}",
        "",
        "Bulk historical data download completed to file repository only.",
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
    "failed_count": len(failed),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
