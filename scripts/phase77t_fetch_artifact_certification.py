#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import csv
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE_FETCH = ARCH / "real_historical_bar_fixture" / "77R_fetch_one_symbol_read_only_bars_latest.json"
SOURCE_RELOCK = ARCH / "fetch_gate_relock" / "77S_fetch_gate_relock_latest.json"
CSV_FILE = ARCH / "real_historical_bar_fixture" / "VFV_TO_1y_1d_max300_read_only.csv"

OUT_DIR = ARCH / "fetch_artifact_certification"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "77T_fetch_artifact_certification_latest.json"
OUT_TXT = OUT_DIR / "77T_fetch_artifact_certification_latest.txt"

PHASE = "77T_FETCH_ARTIFACT_CERTIFICATION"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


fetch = read_json(SOURCE_FETCH)
relock = read_json(SOURCE_RELOCK)

rows = []
if CSV_FILE.exists():
    with CSV_FILE.open("r", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

dates = [r.get("date") for r in rows]
symbols = sorted(set(r.get("symbol") for r in rows))

checks = {
    "fetch_source_exists": SOURCE_FETCH.exists(),
    "fetch_source_certified": fetch.get("certified") is True,
    "relock_source_exists": SOURCE_RELOCK.exists(),
    "relock_source_certified": relock.get("certified") is True,
    "csv_exists": CSV_FILE.exists(),
    "rows_present": len(rows) > 0,
    "rows_capped_300": len(rows) <= 300,
    "one_symbol_only": symbols == ["VFV.TO"],
    "dates_strictly_increasing": dates == sorted(dates) and len(dates) == len(set(dates)),
    "ohlc_rules_valid": all(
        float(r["high"]) >= float(r["open"])
        and float(r["high"]) >= float(r["close"])
        and float(r["low"]) <= float(r["open"])
        and float(r["low"]) <= float(r["close"])
        for r in rows
    ),
    "volume_nonnegative": all(int(float(r["volume"])) >= 0 for r in rows),
    "fetch_gate_relocked": relock.get("policy", {}).get("historical_bar_fetch_enabled") is False,
    "real_replay_blocked": relock.get("policy", {}).get("real_historical_replay_enabled") is False,
    "training_blocked": relock.get("policy", {}).get("training_enabled") is False,
    "strategy_db_write_blocked": relock.get("policy", {}).get("strategy_db_write_allowed") is False,
    "promotion_blocked": relock.get("policy", {}).get("promotion_enabled") is False,
    "broker_live_blocked": (
        relock.get("policy", {}).get("broker_execution_enabled") is False
        and relock.get("policy", {}).get("live_execution_enabled") is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "FETCH_ARTIFACT_CERTIFICATION",
    "source_fetch": str(SOURCE_FETCH),
    "source_relock": str(SOURCE_RELOCK),
    "csv": str(CSV_FILE),
    "row_count": len(rows),
    "symbols": symbols,
    "date_min": min(dates) if dates else None,
    "date_max": max(dates) if dates else None,
    "checks": checks,
    "policy": {
        "fetch_artifact_certified": True,
        "historical_bar_fetch_enabled": False,
        "real_historical_replay_enabled": False,
        "training_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "77U_REAL_HISTORICAL_FETCH_ROLLUP_CERTIFICATION",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"row_count: {result['row_count']}",
        f"symbols: {symbols}",
        f"date_min: {result['date_min']}",
        f"date_max: {result['date_max']}",
        "",
        "Fetch gate remains relocked.",
        "Replay/training/db/promotion/broker/live remain blocked.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "row_count": result["row_count"],
    "symbols": symbols,
    "date_min": result["date_min"],
    "date_max": result["date_max"],
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
