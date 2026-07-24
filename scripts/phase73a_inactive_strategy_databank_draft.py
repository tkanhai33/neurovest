#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "read_only_result_store" / "72A_read_only_result_store_latest.json"
RESULT = ARCH / "read_only_result_store" / "store" / "fixture_ohlcv_v1_metric_result_read_only.json"

OUT_DIR = ARCH / "inactive_strategy_databank_draft"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "73A_inactive_strategy_databank_draft_latest.json"
OUT_TXT = OUT_DIR / "73A_inactive_strategy_databank_draft_latest.txt"

PHASE = "73A_INACTIVE_STRATEGY_DATABANK_DRAFT"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)
stored_result = read_json(RESULT)

draft_record = {
    "databank_record_id": "INACTIVE_DRAFT_FIXTURE_0001",
    "status": "INACTIVE_DRAFT_ONLY",
    "source_result_record": stored_result.get("record_id"),
    "dataset_id": stored_result.get("dataset_id"),
    "row_count": stored_result.get("row_count"),
    "metrics_reference": str(RESULT),
    "activation_state": "NOT_ELIGIBLE",
    "promotion_state": "BLOCKED",
    "manual_gate_required": True,
    "training_eligible": False,
    "broker_eligible": False,
    "live_eligible": False,
    "policy": {
        "inactive_databank_draft_allowed": True,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "automatic_activation_allowed": False,
        "training_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
}

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "stored_result_exists": RESULT.exists(),
    "stored_result_present": bool(stored_result),
    "draft_record_present": bool(draft_record),
    "inactive_only": draft_record["status"] == "INACTIVE_DRAFT_ONLY",
    "not_eligible_for_activation": draft_record["activation_state"] == "NOT_ELIGIBLE",
    "promotion_blocked": draft_record["promotion_state"] == "BLOCKED",
    "manual_gate_required": draft_record["manual_gate_required"] is True,
    "training_blocked": draft_record["training_eligible"] is False,
    "broker_live_blocked": (
        draft_record["broker_eligible"] is False
        and draft_record["live_eligible"] is False
    ),
    "strategy_db_write_blocked": draft_record["policy"]["strategy_db_write_allowed"] is False,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "INACTIVE_STRATEGY_DATABANK_DRAFT_ONLY",
    "source_result_store": str(SOURCE),
    "source_result_record": str(RESULT),
    "draft_record": draft_record,
    "checks": checks,
    "recommended_next_phase": "74A_LEARNING_TRAINING_ARCHITECTURE_PLANNING",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"databank_record_id: {draft_record['databank_record_id']}",
        f"status: {draft_record['status']}",
        "",
        "Still blocked:",
        "- strategy DB write",
        "- promotion",
        "- automatic activation",
        "- training",
        "- broker/live",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "databank_record_id": draft_record["databank_record_id"],
    "status": draft_record["status"],
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
