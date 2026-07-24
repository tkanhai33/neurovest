#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
from collections import Counter
import csv, json, math

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"
RESEARCH_ROOT = ROOT / "backend/app/stacks/learning_research/research_data"

SOURCE = ARCH / "research_repository_numeric_anomaly_inspection/118B_research_repository_numeric_anomaly_inspection_latest.json"

OUT_DIR = ARCH / "research_repository_full_anomaly_export"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "118C_research_repository_full_anomaly_export_latest.json"
OUT_TXT = OUT_DIR / "118C_research_repository_full_anomaly_export_latest.txt"
OUT_CSV = OUT_DIR / "118C_full_anomaly_export.csv"

PHASE = "118C_RESEARCH_REPOSITORY_FULL_ANOMALY_EXPORT"

PRICE_MIN = 0.0
PRICE_MAX = 1_000_000.0
VOLUME_MIN = 0
DAILY_RETURN_MIN = -0.95
DAILY_RETURN_MAX = 10.0

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def finite_number(value):
    try:
        x = float(value)
        return math.isfinite(x)
    except Exception:
        return False

def f(value):
    return float(value)

source = read_json(SOURCE)

csv_files = sorted(RESEARCH_ROOT.rglob("*.csv"))

anomalies = []
reason_counts = Counter()
symbol_counts = Counter()
file_counts = Counter()
asset_group_counts = Counter()

for path in csv_files:
    previous_close = None
    previous_date = None

    try:
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            required = {"date", "open", "high", "low", "close", "volume"}
            missing = required - set(reader.fieldnames or [])

            if missing:
                anomalies.append({
                    "file": str(path),
                    "line": None,
                    "symbol": path.stem,
                    "date": None,
                    "reason": "missing_required_columns",
                    "details": json.dumps({"missing": sorted(missing)}),
                })
                continue

            for line_number, row in enumerate(reader, start=2):
                symbol = row.get("symbol") or path.stem
                date = row.get("date")

                def add(reason, details):
                    parts = Path(path).parts
                    asset_group = "unknown"
                    if "research_data" in parts:
                        idx = parts.index("research_data")
                        if idx + 1 < len(parts):
                            asset_group = parts[idx + 1]

                    item = {
                        "file": str(path),
                        "line": line_number,
                        "asset_group": asset_group,
                        "symbol": symbol,
                        "date": date,
                        "reason": reason,
                        "details": json.dumps(details, sort_keys=True),
                    }
                    anomalies.append(item)
                    reason_counts[reason] += 1
                    symbol_counts[symbol] += 1
                    file_counts[str(path)] += 1
                    asset_group_counts[asset_group] += 1

                fields = ["open", "high", "low", "close", "volume"]
                non_finite = [field for field in fields if not finite_number(row.get(field))]

                if non_finite:
                    add("not_finite_number", {
                        "fields": non_finite,
                        "values": {field: row.get(field) for field in non_finite},
                    })
                    continue

                open_price = f(row["open"])
                high = f(row["high"])
                low = f(row["low"])
                close = f(row["close"])
                volume = f(row["volume"])

                for field, value in {
                    "open": open_price,
                    "high": high,
                    "low": low,
                    "close": close,
                }.items():
                    if not (PRICE_MIN < value < PRICE_MAX):
                        add("price_out_of_bounds", {
                            "field": field,
                            "value": value,
                            "min_exclusive": PRICE_MIN,
                            "max_exclusive": PRICE_MAX,
                        })

                if volume < VOLUME_MIN:
                    add("negative_volume", {
                        "volume": volume,
                    })

                if low > high:
                    add("low_greater_than_high", {
                        "low": low,
                        "high": high,
                    })

                if not (low <= close <= high):
                    add("close_outside_high_low_range", {
                        "low": low,
                        "high": high,
                        "close": close,
                    })

                if previous_close and previous_close > 0:
                    daily_return = (close / previous_close) - 1.0
                    if not (DAILY_RETURN_MIN <= daily_return <= DAILY_RETURN_MAX):
                        add("daily_return_out_of_bounds", {
                            "previous_date": previous_date,
                            "previous_close": previous_close,
                            "close": close,
                            "daily_return": daily_return,
                            "min": DAILY_RETURN_MIN,
                            "max": DAILY_RETURN_MAX,
                        })

                previous_close = close
                previous_date = date

    except Exception as exc:
        anomalies.append({
            "file": str(path),
            "line": None,
            "asset_group": "unknown",
            "symbol": path.stem,
            "date": None,
            "reason": "scan_exception",
            "details": json.dumps({"error": str(exc)}),
        })
        reason_counts["scan_exception"] += 1
        symbol_counts[path.stem] += 1
        file_counts[str(path)] += 1

with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=[
        "file", "line", "asset_group", "symbol", "date", "reason", "details"
    ])
    writer.writeheader()
    writer.writerows(anomalies)

inspection = source.get("inspection", {})

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "research_root_exists": RESEARCH_ROOT.exists(),
    "csv_files_scanned_at_least_144": len(csv_files) >= 144,
    "anomalies_exported": len(anomalies) > 0,
    "export_csv_written": OUT_CSV.exists(),
    "matches_118a_bad_count": len(anomalies) == inspection.get("source_bad_count"),
    "reason_counts_present": len(reason_counts) > 0,
    "db_write_blocked": True,
    "training_blocked": True,
    "broker_live_blocked": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "files_scanned": len(csv_files),
    "anomaly_count": len(anomalies),
    "export_csv": str(OUT_CSV),
    "reason_counts": dict(reason_counts),
    "top_symbols": symbol_counts.most_common(50),
    "top_files": file_counts.most_common(50),
    "asset_group_counts": dict(asset_group_counts),
    "anomaly_sample": anomalies[:100],
    "checks": checks,
    "policy": {
        "full_anomaly_export_executed": True,
        "data_modification_allowed": False,
        "approved_for_training": False,
        "database_writes_allowed": False,
        "training_execution_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "118D_RESEARCH_REPOSITORY_ANOMALY_CLASSIFICATION_POLICY",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"files_scanned: {len(csv_files)}",
        f"anomaly_count: {len(anomalies)}",
        f"reason_counts: {dict(reason_counts)}",
        f"export_csv: {OUT_CSV}",
        "",
        "Full anomaly export completed.",
        "No data modification. No DB writes. No training. No broker/live.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "files_scanned": len(csv_files),
    "anomaly_count": len(anomalies),
    "reason_counts": dict(reason_counts),
    "export_csv": str(OUT_CSV),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
