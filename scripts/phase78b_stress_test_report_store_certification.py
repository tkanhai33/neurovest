#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "stress_test_report_store" / "78A_stress_test_report_store_latest.json"
REPORT = ARCH / "stress_test_report_store" / "store" / "VFV_TO_stress_test_report_read_only.json"

OUT_DIR = ARCH / "stress_test_report_store_certification"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "78B_stress_test_report_store_certification_latest.json"
OUT_TXT = OUT_DIR / "78B_stress_test_report_store_certification_latest.txt"

PHASE = "78B_STRESS_TEST_REPORT_STORE_CERTIFICATION"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)
report = read_json(REPORT)
stress = report.get("stress_tests", {})
policy = report.get("policy", {})

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "report_exists": REPORT.exists(),
    "report_present": bool(report),
    "report_id_present": bool(report.get("report_id")),
    "symbol_correct": report.get("symbol") == "VFV.TO",
    "row_count_present": report.get("row_count", 0) > 0,
    "row_count_capped_300": report.get("row_count", 0) <= 300,
    "stress_tests_present": bool(stress),
    "return_series_created": stress.get("return_series_created") is True,
    "row_count_check_passed": stress.get("row_count_check") is True,
    "cumulative_return_present": isinstance(stress.get("cumulative_return"), float),
    "max_drawdown_present": isinstance(stress.get("max_drawdown"), float),
    "read_only_report": policy.get("read_only_stress_report") is True,
    "real_replay_blocked": policy.get("real_historical_replay_enabled") is False,
    "training_blocked": policy.get("training_enabled") is False,
    "strategy_db_write_blocked": policy.get("strategy_db_write_allowed") is False,
    "promotion_blocked": policy.get("promotion_enabled") is False,
    "broker_live_blocked": (
        policy.get("broker_execution_enabled") is False
        and policy.get("live_execution_enabled") is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "STRESS_TEST_REPORT_STORE_CERTIFICATION",
    "source_store": str(SOURCE),
    "report": str(REPORT),
    "report_summary": {
        "report_id": report.get("report_id"),
        "symbol": report.get("symbol"),
        "row_count": report.get("row_count"),
        "cumulative_return": stress.get("cumulative_return"),
        "max_drawdown": stress.get("max_drawdown"),
        "negative_return_days": stress.get("negative_return_days"),
        "positive_return_days": stress.get("positive_return_days"),
    },
    "checks": checks,
    "policy": {
        "stress_test_report_store_certified": True,
        "real_historical_replay_enabled": False,
        "training_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "78C_STRESS_TEST_REPORT_ROLLUP_CERTIFICATION",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"report_id: {result['report_summary']['report_id']}",
        f"symbol: {result['report_summary']['symbol']}",
        f"row_count: {result['report_summary']['row_count']}",
        "",
        "Stress report certified read-only.",
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
    "report_summary": result["report_summary"],
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
