#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import csv
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "fixture_bar_dataset" / "68B_fixture_bar_dataset_source_creation_latest.json"

OUT_DIR = ARCH / "fixture_bar_dataset"
OUT_JSON = OUT_DIR / "68C_fixture_bar_dataset_validation_latest.json"
OUT_TXT = OUT_DIR / "68C_fixture_bar_dataset_validation_latest.txt"

PHASE = "68C_FIXTURE_BAR_DATASET_VALIDATION"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)
csv_path = Path(source.get("fixture_csv", ""))

rows = []
with csv_path.open("r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

dates = [r["date"] for r in rows]

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "csv_exists": csv_path.exists(),
    "row_count_is_10": len(rows) == 10,
    "columns_valid": list(rows[0].keys()) == ["symbol", "date", "open", "high", "low", "close", "volume"] if rows else False,
    "dates_strictly_increasing": dates == sorted(dates) and len(dates) == len(set(dates)),
    "ohlc_rules_valid": all(
        float(r["high"]) >= float(r["open"])
        and float(r["high"]) >= float(r["close"])
        and float(r["low"]) <= float(r["open"])
        and float(r["low"]) <= float(r["close"])
        for r in rows
    ),
    "volume_nonnegative": all(int(r["volume"]) >= 0 for r in rows),
    "historical_replay_blocked": True,
    "runtime_execution_blocked": True,
    "strategy_db_write_blocked": True,
    "promotion_blocked": True,
    "broker_live_blocked": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "FIXTURE_BAR_DATASET_VALIDATION_ONLY",
    "source_creation": str(SOURCE),
    "fixture_csv": str(csv_path),
    "row_count": len(rows),
    "checks": checks,
    "policy": {
        "fixture_validation_allowed": True,
        "historical_replay_allowed_now": False,
        "runtime_execution_allowed": False,
        "runtime_mutation_allowed": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "68D_FIXTURE_BAR_DATASET_ROLLUP_CERTIFICATION",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"row_count: {len(rows)}",
        f"fixture_csv: {csv_path}",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "row_count": len(rows),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
