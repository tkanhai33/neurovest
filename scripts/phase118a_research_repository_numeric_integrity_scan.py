#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import csv, json, math

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"
RESEARCH_ROOT = ROOT / "backend/app/stacks/learning_research/research_data"

SOURCE = ARCH / "research_repository_download_rollup/117L_research_repository_download_rollup_latest.json"

OUT_DIR = ARCH / "research_repository_numeric_integrity_scan"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "118A_research_repository_numeric_integrity_scan_latest.json"
OUT_TXT = OUT_DIR / "118A_research_repository_numeric_integrity_scan_latest.txt"

PHASE = "118A_RESEARCH_REPOSITORY_NUMERIC_INTEGRITY_SCAN"

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

files_scanned = 0
rows_scanned = 0
bad = []
symbol_summaries = []

for path in csv_files:
    files_scanned += 1
    previous_close = None
    previous_date = None
    row_count = 0
    symbol = path.stem

    try:
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            required = {"date", "open", "high", "low", "close", "volume"}
            missing = required - set(reader.fieldnames or [])
            if missing:
                bad.append({
                    "file": str(path),
                    "reason": "missing_required_columns",
                    "missing": sorted(missing),
                })
                continue

            for line_number, row in enumerate(reader, start=2):
                row_count += 1
                rows_scanned += 1

                symbol = row.get("symbol") or path.stem
                date = row.get("date")

                for field in ["open", "high", "low", "close", "volume"]:
                    if not finite_number(row.get(field)):
                        bad.append({
                            "file": str(path),
                            "line": line_number,
                            "symbol": symbol,
                            "date": date,
                            "field": field,
                            "value": row.get(field),
                            "reason": "not_finite_number",
                        })

                if all(finite_number(row.get(field)) for field in ["open", "high", "low", "close", "volume"]):
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
                            bad.append({
                                "file": str(path),
                                "line": line_number,
                                "symbol": symbol,
                                "date": date,
                                "field": field,
                                "value": value,
                                "reason": "price_out_of_bounds",
                            })

                    if volume < VOLUME_MIN:
                        bad.append({
                            "file": str(path),
                            "line": line_number,
                            "symbol": symbol,
                            "date": date,
                            "field": "volume",
                            "value": volume,
                            "reason": "negative_volume",
                        })

                    if low > high:
                        bad.append({
                            "file": str(path),
                            "line": line_number,
                            "symbol": symbol,
                            "date": date,
                            "low": low,
                            "high": high,
                            "reason": "low_greater_than_high",
                        })

                    if not (low <= close <= high):
                        bad.append({
                            "file": str(path),
                            "line": line_number,
                            "symbol": symbol,
                            "date": date,
                            "close": close,
                            "low": low,
                            "high": high,
                            "reason": "close_outside_high_low_range",
                        })

                    if previous_close and previous_close > 0:
                        daily_return = (close / previous_close) - 1.0
                        if not (DAILY_RETURN_MIN <= daily_return <= DAILY_RETURN_MAX):
                            bad.append({
                                "file": str(path),
                                "line": line_number,
                                "symbol": symbol,
                                "previous_date": previous_date,
                                "date": date,
                                "previous_close": previous_close,
                                "close": close,
                                "daily_return": daily_return,
                                "reason": "daily_return_out_of_bounds",
                            })

                    previous_close = close
                    previous_date = date

        symbol_summaries.append({
            "file": str(path),
            "symbol": symbol,
            "rows": row_count,
        })

    except Exception as exc:
        bad.append({
            "file": str(path),
            "reason": "scan_exception",
            "error": str(exc),
        })

bad_reasons = {}
for item in bad:
    bad_reasons[item["reason"]] = bad_reasons.get(item["reason"], 0) + 1

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "research_root_exists": RESEARCH_ROOT.exists(),
    "csv_files_scanned_at_least_144": files_scanned >= 144,
    "rows_scanned": rows_scanned > 0,
    "no_bad_numeric_events": len(bad) == 0,
    "no_nan_or_infinity": bad_reasons.get("not_finite_number", 0) == 0,
    "prices_within_bounds": bad_reasons.get("price_out_of_bounds", 0) == 0,
    "volume_non_negative": bad_reasons.get("negative_volume", 0) == 0,
    "ohlc_consistent": (
        bad_reasons.get("low_greater_than_high", 0) == 0
        and bad_reasons.get("close_outside_high_low_range", 0) == 0
    ),
    "daily_returns_within_bounds": bad_reasons.get("daily_return_out_of_bounds", 0) == 0,
    "db_write_blocked": True,
    "training_blocked": True,
    "broker_live_blocked": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "limits": {
        "price_min_exclusive": PRICE_MIN,
        "price_max_exclusive": PRICE_MAX,
        "volume_min": VOLUME_MIN,
        "daily_return_min": DAILY_RETURN_MIN,
        "daily_return_max": DAILY_RETURN_MAX,
    },
    "files_scanned": files_scanned,
    "rows_scanned": rows_scanned,
    "bad_count": len(bad),
    "bad_reasons": bad_reasons,
    "bad_sample": bad[:100],
    "symbol_summaries_sample": symbol_summaries[:50],
    "checks": checks,
    "policy": {
        "numeric_integrity_scan_executed": True,
        "approved_for_training": False,
        "database_writes_allowed": False,
        "training_execution_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "118B_RESEARCH_REPOSITORY_NUMERIC_ANOMALY_INSPECTION",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"files_scanned: {files_scanned}",
        f"rows_scanned: {rows_scanned}",
        f"bad_count: {len(bad)}",
        f"bad_reasons: {bad_reasons}",
        "",
        "Research repository numeric integrity scan completed.",
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
    "files_scanned": files_scanned,
    "rows_scanned": rows_scanned,
    "bad_count": len(bad),
    "bad_reasons": bad_reasons,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
