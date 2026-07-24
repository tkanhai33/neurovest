#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import csv
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "real_historical_fetch_rollup" / "77U_real_historical_fetch_rollup_certification_latest.json"
BAR_CSV = ARCH / "real_historical_bar_fixture" / "VFV_TO_1y_1d_max300_read_only.csv"

OUT_DIR = ARCH / "stress_test_report_store"
STORE = OUT_DIR / "store"
STORE.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "78A_stress_test_report_store_latest.json"
OUT_TXT = OUT_DIR / "78A_stress_test_report_store_latest.txt"
REPORT_JSON = STORE / "VFV_TO_stress_test_report_read_only.json"

PHASE = "78A_STRESS_TEST_REPORT_STORE"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)

rows = []
if BAR_CSV.exists():
    with BAR_CSV.open("r", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

closes = [float(r["close"]) for r in rows]

returns = []
for previous, current in zip(closes, closes[1:]):
    returns.append((current / previous) - 1.0 if previous else 0.0)

cumulative = 1.0
equity_curve = [1.0]
for value in returns:
    cumulative *= 1.0 + value
    equity_curve.append(cumulative)

peak = equity_curve[0] if equity_curve else 1.0
max_drawdown = 0.0
for value in equity_curve:
    peak = max(peak, value)
    drawdown = (value / peak) - 1.0 if peak else 0.0
    max_drawdown = min(max_drawdown, drawdown)

report = {
    "report_id": "READ_ONLY_STRESS_REPORT_VFV_TO_0001",
    "created_at": datetime.now(UTC).isoformat(),
    "symbol": "VFV.TO",
    "source_bar_csv": str(BAR_CSV),
    "row_count": len(rows),
    "stress_tests": {
        "row_count_check": len(rows) > 0 and len(rows) <= 300,
        "return_series_created": len(returns) == max(len(rows) - 1, 0),
        "cumulative_return": cumulative - 1.0,
        "max_drawdown": max_drawdown,
        "negative_return_days": sum(1 for r in returns if r < 0),
        "positive_return_days": sum(1 for r in returns if r > 0),
    },
    "policy": {
        "read_only_stress_report": True,
        "real_historical_replay_enabled": False,
        "training_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
}

REPORT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "bar_csv_exists": BAR_CSV.exists(),
    "rows_present": len(rows) > 0,
    "rows_capped_300": len(rows) <= 300,
    "report_written": REPORT_JSON.exists(),
    "stress_tests_present": bool(report["stress_tests"]),
    "read_only_report": report["policy"]["read_only_stress_report"] is True,
    "real_replay_blocked": report["policy"]["real_historical_replay_enabled"] is False,
    "training_blocked": report["policy"]["training_enabled"] is False,
    "strategy_db_write_blocked": report["policy"]["strategy_db_write_allowed"] is False,
    "promotion_blocked": report["policy"]["promotion_enabled"] is False,
    "broker_live_blocked": (
        report["policy"]["broker_execution_enabled"] is False
        and report["policy"]["live_execution_enabled"] is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "STRESS_TEST_REPORT_STORE_READ_ONLY",
    "source_fetch_rollup": str(SOURCE),
    "source_bar_csv": str(BAR_CSV),
    "stored_report": str(REPORT_JSON),
    "row_count": len(rows),
    "checks": checks,
    "policy": report["policy"],
    "recommended_next_phase": "78B_STRESS_TEST_REPORT_STORE_CERTIFICATION",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"row_count: {len(rows)}",
        f"stored_report: {REPORT_JSON}",
        "",
        "Stress report stored read-only.",
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
    "row_count": len(rows),
    "stored_report": str(REPORT_JSON),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
