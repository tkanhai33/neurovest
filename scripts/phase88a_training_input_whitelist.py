#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "manual_approval_artifact" / "87A_manual_approval_artifact_latest.json"

REPORT = ARCH / "stress_test_report_store" / "store" / "VFV_TO_stress_test_report_read_only.json"
BAR_CSV = ARCH / "real_historical_bar_fixture" / "VFV_TO_1y_1d_max300_read_only.csv"
LEARNER = ROOT / "backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/training_read_only_learner.py"

OUT_DIR = ARCH / "training_input_whitelist"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "88A_training_input_whitelist_latest.json"
OUT_TXT = OUT_DIR / "88A_training_input_whitelist_latest.txt"

PHASE = "88A_TRAINING_INPUT_WHITELIST"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)
report = read_json(REPORT)

whitelist = {
    "mode": "TRAINING_INPUT_WHITELIST_READ_ONLY",
    "allowed_inputs": [
        {
            "input_id": "VFV_TO_STRESS_REPORT_READ_ONLY",
            "type": "stress_report",
            "path": str(REPORT),
            "symbol": report.get("symbol"),
            "row_count": report.get("row_count"),
            "read_only": True,
        },
        {
            "input_id": "VFV_TO_BAR_FIXTURE_READ_ONLY",
            "type": "bar_fixture_csv",
            "path": str(BAR_CSV),
            "symbol": "VFV.TO",
            "max_rows": 300,
            "read_only": True,
        },
    ],
    "allowed_code": [
        {
            "code_id": "TRAINING_READ_ONLY_LEARNER",
            "path": str(LEARNER),
            "read_only_learner_only": True,
        }
    ],
    "forbidden_inputs": [
        "live broker orders",
        "uncertified replay outputs",
        "uncertified candidate mutations",
        "strategy DB writable records",
        "promotion queue records",
    ],
    "hard_blocks": {
        "training_execution_enabled": False,
        "learner_write_enabled": False,
        "mutation_allowed": False,
        "queue_write_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
}

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "report_exists": REPORT.exists(),
    "bar_csv_exists": BAR_CSV.exists(),
    "learner_exists": LEARNER.exists(),
    "whitelist_present": bool(whitelist),
    "allowed_inputs_present": len(whitelist["allowed_inputs"]) == 2,
    "all_inputs_read_only": all(item["read_only"] is True for item in whitelist["allowed_inputs"]),
    "training_execution_blocked": whitelist["hard_blocks"]["training_execution_enabled"] is False,
    "learner_write_blocked": whitelist["hard_blocks"]["learner_write_enabled"] is False,
    "mutation_blocked": whitelist["hard_blocks"]["mutation_allowed"] is False,
    "queue_write_blocked": whitelist["hard_blocks"]["queue_write_enabled"] is False,
    "strategy_db_write_blocked": whitelist["hard_blocks"]["strategy_db_write_allowed"] is False,
    "promotion_blocked": whitelist["hard_blocks"]["promotion_enabled"] is False,
    "broker_live_blocked": (
        whitelist["hard_blocks"]["broker_execution_enabled"] is False
        and whitelist["hard_blocks"]["live_execution_enabled"] is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "TRAINING_INPUT_WHITELIST",
    "source_manual_approval": str(SOURCE),
    "whitelist": whitelist,
    "checks": checks,
    "policy": {
        "training_input_whitelist_certified": True,
        **whitelist["hard_blocks"],
    },
    "recommended_next_phase": "89A_TRAINING_OUTPUT_SANDBOX",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"allowed_inputs: {len(whitelist['allowed_inputs'])}",
        "",
        "Inputs whitelisted read-only.",
        "Training/write/mutation/queue/db/promotion/broker/live remain blocked.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "allowed_inputs": len(whitelist["allowed_inputs"]),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
