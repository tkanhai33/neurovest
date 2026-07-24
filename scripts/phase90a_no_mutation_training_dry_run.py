#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json
import statistics

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE_WHITELIST = ARCH / "training_input_whitelist" / "88A_training_input_whitelist_latest.json"
SOURCE_SANDBOX = ARCH / "training_output_sandbox" / "89A_training_output_sandbox_latest.json"
REPORT = ARCH / "stress_test_report_store" / "store" / "VFV_TO_stress_test_report_read_only.json"

OUT_DIR = ARCH / "no_mutation_training_dry_run"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "90A_no_mutation_training_dry_run_latest.json"
OUT_TXT = OUT_DIR / "90A_no_mutation_training_dry_run_latest.txt"

PHASE = "90A_NO_MUTATION_TRAINING_DRY_RUN"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


whitelist = read_json(SOURCE_WHITELIST)
sandbox = read_json(SOURCE_SANDBOX)
report = read_json(REPORT)
stress = report.get("stress_tests", {})

observations = {
    "symbol": report.get("symbol"),
    "row_count": report.get("row_count"),
    "cumulative_return": stress.get("cumulative_return"),
    "max_drawdown": stress.get("max_drawdown"),
    "negative_return_days": stress.get("negative_return_days"),
    "positive_return_days": stress.get("positive_return_days"),
}

training_dry_run = {
    "mode": "NO_MUTATION_TRAINING_DRY_RUN",
    "training_executed": False,
    "inspection_executed": True,
    "candidate_mutation_created": False,
    "learner_write_executed": False,
    "queue_write_executed": False,
    "strategy_db_write_executed": False,
    "promotion_executed": False,
    "broker_execution_executed": False,
    "live_execution_executed": False,
    "observations": observations,
    "dry_run_interpretation": {
        "positive_return_days_exceed_negative": (
            observations["positive_return_days"] > observations["negative_return_days"]
            if observations["positive_return_days"] is not None and observations["negative_return_days"] is not None
            else False
        ),
        "max_drawdown_observed": observations["max_drawdown"],
        "training_action": "NO_ACTION_READ_ONLY_INSPECTION_ONLY",
    },
}

checks = {
    "whitelist_exists": SOURCE_WHITELIST.exists(),
    "whitelist_certified": whitelist.get("certified") is True,
    "sandbox_exists": SOURCE_SANDBOX.exists(),
    "sandbox_certified": sandbox.get("certified") is True,
    "report_exists": REPORT.exists(),
    "report_present": bool(report),
    "inspection_executed": training_dry_run["inspection_executed"] is True,
    "training_not_executed": training_dry_run["training_executed"] is False,
    "mutation_not_created": training_dry_run["candidate_mutation_created"] is False,
    "learner_write_not_executed": training_dry_run["learner_write_executed"] is False,
    "queue_write_not_executed": training_dry_run["queue_write_executed"] is False,
    "strategy_db_write_not_executed": training_dry_run["strategy_db_write_executed"] is False,
    "promotion_not_executed": training_dry_run["promotion_executed"] is False,
    "broker_live_not_executed": (
        training_dry_run["broker_execution_executed"] is False
        and training_dry_run["live_execution_executed"] is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "NO_MUTATION_TRAINING_DRY_RUN",
    "source_whitelist": str(SOURCE_WHITELIST),
    "source_sandbox": str(SOURCE_SANDBOX),
    "source_report": str(REPORT),
    "training_dry_run": training_dry_run,
    "checks": checks,
    "policy": {
        "no_mutation_training_dry_run_certified": True,
        "training_execution_enabled": False,
        "learner_write_enabled": False,
        "mutation_allowed": False,
        "queue_write_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "91A_NO_DB_NO_PROMOTION_NO_BROKER_CERTIFICATION",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"symbol: {observations['symbol']}",
        f"row_count: {observations['row_count']}",
        f"training_executed: {training_dry_run['training_executed']}",
        f"inspection_executed: {training_dry_run['inspection_executed']}",
        "",
        "No mutation. No writes. No promotion. No broker/live.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "symbol": observations["symbol"],
    "row_count": observations["row_count"],
    "training_executed": training_dry_run["training_executed"],
    "inspection_executed": training_dry_run["inspection_executed"],
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
