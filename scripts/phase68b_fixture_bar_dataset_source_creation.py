#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import csv
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "fixture_bar_dataset" / "68A_fixture_bar_dataset_manifest_latest.json"

OUT_DIR = ARCH / "fixture_bar_dataset"
DATA_DIR = OUT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "68B_fixture_bar_dataset_source_creation_latest.json"
OUT_TXT = OUT_DIR / "68B_fixture_bar_dataset_source_creation_latest.txt"
OUT_CSV = DATA_DIR / "fixture_ohlcv_v1.csv"

PHASE = "68B_FIXTURE_BAR_DATASET_SOURCE_CREATION"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)

rows = [
    ["FIXTURE.TO", "2024-01-02", 100.00, 102.00, 99.00, 101.00, 1000],
    ["FIXTURE.TO", "2024-01-03", 101.00, 103.00, 100.00, 102.50, 1200],
    ["FIXTURE.TO", "2024-01-04", 102.50, 104.00, 101.50, 103.00, 1100],
    ["FIXTURE.TO", "2024-01-05", 103.00, 105.00, 102.00, 104.50, 1300],
    ["FIXTURE.TO", "2024-01-08", 104.50, 106.00, 103.50, 105.00, 1250],
    ["FIXTURE.TO", "2024-01-09", 105.00, 107.00, 104.00, 106.50, 1400],
    ["FIXTURE.TO", "2024-01-10", 106.50, 108.00, 105.50, 107.00, 1350],
    ["FIXTURE.TO", "2024-01-11", 107.00, 109.00, 106.00, 108.50, 1500],
    ["FIXTURE.TO", "2024-01-12", 108.50, 110.00, 107.50, 109.00, 1450],
    ["FIXTURE.TO", "2024-01-15", 109.00, 111.00, 108.00, 110.50, 1600],
]

with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["symbol", "date", "open", "high", "low", "close", "volume"])
    writer.writerows(rows)

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "csv_created": OUT_CSV.exists(),
    "row_count_matches_manifest": len(rows) == source.get("fixture_manifest", {}).get("rows_planned"),
    "columns_match_manifest": source.get("fixture_manifest", {}).get("columns_required") == ["symbol", "date", "open", "high", "low", "close", "volume"],
    "high_low_rules_pass": all(r[3] >= r[2] and r[3] >= r[5] and r[4] <= r[2] and r[4] <= r[5] for r in rows),
    "volume_nonnegative": all(r[6] >= 0 for r in rows),
    "historical_replay_blocked": True,
    "runtime_execution_blocked": True,
    "strategy_db_write_blocked": True,
    "promotion_blocked": True,
    "broker_live_blocked": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "FIXTURE_BAR_DATASET_SOURCE_CREATION_ONLY",
    "source_manifest": str(SOURCE),
    "fixture_csv": str(OUT_CSV),
    "row_count": len(rows),
    "policy": {
        "fixture_file_write_allowed": True,
        "historical_replay_allowed_now": False,
        "runtime_execution_allowed": False,
        "runtime_mutation_allowed": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": checks,
    "recommended_next_phase": "68C_FIXTURE_BAR_DATASET_VALIDATION",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"fixture_csv: {OUT_CSV}",
        f"row_count: {len(rows)}",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "fixture_csv": str(OUT_CSV),
    "row_count": len(rows),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
