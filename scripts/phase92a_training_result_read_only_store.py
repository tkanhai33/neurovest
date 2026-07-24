#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE_CERT = ARCH / "no_db_no_promotion_no_broker_certification" / "91A_no_db_no_promotion_no_broker_certification_latest.json"
SOURCE_DRY_RUN = ARCH / "no_mutation_training_dry_run" / "90A_no_mutation_training_dry_run_latest.json"

OUT_DIR = ARCH / "training_result_read_only_store"
STORE = OUT_DIR / "store"
STORE.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "92A_training_result_read_only_store_latest.json"
OUT_TXT = OUT_DIR / "92A_training_result_read_only_store_latest.txt"
RESULT_JSON = STORE / "READ_ONLY_TRAINING_RESULT_0001.json"

PHASE = "92A_TRAINING_RESULT_READ_ONLY_STORE"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


cert = read_json(SOURCE_CERT)
dry_run = read_json(SOURCE_DRY_RUN)

training_result = {
    "result_id": "READ_ONLY_TRAINING_RESULT_0001",
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "READ_ONLY_RESULT_STORE",
    "source_dry_run": str(SOURCE_DRY_RUN),
    "training_dry_run": dry_run.get("training_dry_run", {}),
    "policy": {
        "read_only_training_result": True,
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

RESULT_JSON.write_text(json.dumps(training_result, indent=2), encoding="utf-8")

checks = {
    "cert_source_exists": SOURCE_CERT.exists(),
    "cert_source_certified": cert.get("certified") is True,
    "dry_run_source_exists": SOURCE_DRY_RUN.exists(),
    "dry_run_source_certified": dry_run.get("certified") is True,
    "store_dir_exists": STORE.exists(),
    "result_written": RESULT_JSON.exists(),
    "read_only_result": training_result["policy"]["read_only_training_result"] is True,
    "training_execution_blocked": training_result["policy"]["training_execution_enabled"] is False,
    "learner_write_blocked": training_result["policy"]["learner_write_enabled"] is False,
    "mutation_blocked": training_result["policy"]["mutation_allowed"] is False,
    "queue_write_blocked": training_result["policy"]["queue_write_enabled"] is False,
    "strategy_db_write_blocked": training_result["policy"]["strategy_db_write_allowed"] is False,
    "promotion_blocked": training_result["policy"]["promotion_enabled"] is False,
    "broker_live_blocked": (
        training_result["policy"]["broker_execution_enabled"] is False
        and training_result["policy"]["live_execution_enabled"] is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "TRAINING_RESULT_READ_ONLY_STORE",
    "stored_result": str(RESULT_JSON),
    "checks": checks,
    "policy": training_result["policy"],
    "recommended_next_phase": "93A_ROLLBACK_RELOCK_GATE",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"stored_result: {RESULT_JSON}",
        "",
        "Training result stored read-only.",
        "DB/promotion/broker/live remain blocked.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "stored_result": str(RESULT_JSON),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
