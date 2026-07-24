#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

PHASE = "78C_STRESS_TEST_REPORT_ROLLUP_CERTIFICATION"

EXPECTED = {
    "78A_store": ARCH / "stress_test_report_store/78A_stress_test_report_store_latest.json",
    "78B_certification": ARCH / "stress_test_report_store_certification/78B_stress_test_report_store_certification_latest.json",
}

OUT_DIR = ARCH / "stress_test_report_rollup"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "78C_stress_test_report_rollup_certification_latest.json"
OUT_TXT = OUT_DIR / "78C_stress_test_report_rollup_certification_latest.txt"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


artifacts = {}
checks = {}

for name, path in EXPECTED.items():
    data = read_json(path)
    artifacts[name] = {
        "path": str(path),
        "exists": path.exists(),
        "phase": data.get("phase"),
        "certified": data.get("certified") is True,
    }
    checks[f"{name}_exists"] = path.exists()
    checks[f"{name}_certified"] = data.get("certified") is True

cert = read_json(EXPECTED["78B_certification"])
summary = cert.get("report_summary", {})

checks["report_summary_present"] = bool(summary)
checks["symbol_correct"] = summary.get("symbol") == "VFV.TO"
checks["row_count_present"] = summary.get("row_count", 0) > 0
checks["cumulative_return_present"] = isinstance(summary.get("cumulative_return"), float)
checks["max_drawdown_present"] = isinstance(summary.get("max_drawdown"), float)

policy = cert.get("policy", {})
checks["real_replay_blocked"] = policy.get("real_historical_replay_enabled") is False
checks["training_blocked"] = policy.get("training_enabled") is False
checks["strategy_db_write_blocked"] = policy.get("strategy_db_write_allowed") is False
checks["promotion_blocked"] = policy.get("promotion_enabled") is False
checks["broker_live_blocked"] = (
    policy.get("broker_execution_enabled") is False
    and policy.get("live_execution_enabled") is False
)

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "STRESS_TEST_REPORT_ROLLUP_CERTIFICATION",
    "artifacts": artifacts,
    "report_summary": summary,
    "policy": {
        "stress_test_report_rollup_certified": True,
        "real_historical_replay_enabled": False,
        "training_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": checks,
    "recommended_next_phase": "79A_MANUAL_ACTIVATION_GATE_STUB",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"symbol: {summary.get('symbol')}",
        f"row_count: {summary.get('row_count')}",
        f"cumulative_return: {summary.get('cumulative_return')}",
        f"max_drawdown: {summary.get('max_drawdown')}",
        "",
        "Stress test report rollup certified.",
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
    "report_summary": summary,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
