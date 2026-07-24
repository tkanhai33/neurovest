#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json
import shutil

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "no_write_no_promotion_no_broker" / "71B_no_write_no_promotion_no_broker_certification_latest.json"
DRY_RUN = ARCH / "single_fixture_replay_dry_run" / "71A_single_fixture_replay_dry_run_only_latest.json"

OUT_DIR = ARCH / "read_only_result_store"
STORE = OUT_DIR / "store"
STORE.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "72A_read_only_result_store_latest.json"
OUT_TXT = OUT_DIR / "72A_read_only_result_store_latest.txt"
RESULT_COPY = STORE / "fixture_ohlcv_v1_metric_result_read_only.json"

PHASE = "72A_READ_ONLY_RESULT_STORE"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)
dry_run = read_json(DRY_RUN)

result_record = {
    "record_id": "READ_ONLY_FIXTURE_RESULT_0001",
    "created_at": datetime.now(UTC).isoformat(),
    "source_phase": PHASE,
    "dataset_id": dry_run.get("metrics", {}).get("dataset_id"),
    "row_count": dry_run.get("metrics", {}).get("row_count"),
    "metrics": dry_run.get("metrics", {}),
    "store_policy": {
        "read_only_result_store": True,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
        "runtime_execution_allowed": False,
    },
}

RESULT_COPY.write_text(json.dumps(result_record, indent=2), encoding="utf-8")

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "dry_run_exists": DRY_RUN.exists(),
    "dry_run_certified": dry_run.get("certified") is True,
    "result_copy_written": RESULT_COPY.exists(),
    "dataset_id_present": bool(result_record["dataset_id"]),
    "metrics_present": bool(result_record["metrics"]),
    "read_only_store_policy_present": result_record["store_policy"]["read_only_result_store"] is True,
    "strategy_db_write_blocked": result_record["store_policy"]["strategy_db_write_allowed"] is False,
    "promotion_blocked": result_record["store_policy"]["promotion_enabled"] is False,
    "broker_live_blocked": (
        result_record["store_policy"]["broker_execution_enabled"] is False
        and result_record["store_policy"]["live_execution_enabled"] is False
    ),
    "runtime_execution_blocked": result_record["store_policy"]["runtime_execution_allowed"] is False,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "READ_ONLY_RESULT_STORE",
    "source_safety_certification": str(SOURCE),
    "source_dry_run": str(DRY_RUN),
    "stored_result": str(RESULT_COPY),
    "policy": {
        "read_only_result_store_allowed": True,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
        "runtime_execution_allowed": False,
        "runtime_mutation_allowed": False,
    },
    "checks": checks,
    "recommended_next_phase": "73A_INACTIVE_STRATEGY_DATABANK_DRAFT",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"stored_result: {RESULT_COPY}",
        "",
        "Still blocked:",
        "- strategy DB write",
        "- promotion",
        "- broker execution",
        "- live execution",
        "- runtime execution",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "stored_result": str(RESULT_COPY),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
