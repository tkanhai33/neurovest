#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "no_mutation_training_dry_run" / "90A_no_mutation_training_dry_run_latest.json"

OUT_DIR = ARCH / "no_db_no_promotion_no_broker_certification"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "91A_no_db_no_promotion_no_broker_certification_latest.json"
OUT_TXT = OUT_DIR / "91A_no_db_no_promotion_no_broker_certification_latest.txt"

PHASE = "91A_NO_DB_NO_PROMOTION_NO_BROKER_CERTIFICATION"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)
dry_run = source.get("training_dry_run", {})

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "training_not_executed": dry_run.get("training_executed") is False,
    "inspection_executed": dry_run.get("inspection_executed") is True,
    "mutation_not_created": dry_run.get("candidate_mutation_created") is False,
    "learner_write_not_executed": dry_run.get("learner_write_executed") is False,
    "queue_write_not_executed": dry_run.get("queue_write_executed") is False,
    "strategy_db_write_not_executed": dry_run.get("strategy_db_write_executed") is False,
    "promotion_not_executed": dry_run.get("promotion_executed") is False,
    "broker_live_not_executed": (
        dry_run.get("broker_execution_executed") is False
        and dry_run.get("live_execution_executed") is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "NO_DB_NO_PROMOTION_NO_BROKER_CERTIFICATION",
    "source_dry_run": str(SOURCE),
    "checks": checks,
    "policy": {
        "no_db_no_promotion_no_broker_certified": True,
        "training_execution_enabled": False,
        "learner_write_enabled": False,
        "mutation_allowed": False,
        "queue_write_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "92A_TRAINING_RESULT_READ_ONLY_STORE",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        "DB writes: blocked",
        "promotion: blocked",
        "broker/live: blocked",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
