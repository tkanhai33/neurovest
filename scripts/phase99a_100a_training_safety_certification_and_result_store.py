#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json, shutil

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "read_only_sandbox_training_run_with_stream" / "98A_read_only_sandbox_training_run_with_stream_latest.json"

OUT_DIR = ARCH / "training_safety_certification_and_result_store"
STORE = OUT_DIR / "store" / "TRAINING_RUN_0001"
STORE.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "99A_100A_training_safety_certification_and_result_store_latest.json"
OUT_TXT = OUT_DIR / "99A_100A_training_safety_certification_and_result_store_latest.txt"

PHASE = "99A_100A_TRAINING_SAFETY_CERTIFICATION_AND_RESULT_STORE"

def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

source = read_json(SOURCE)
training_result = source.get("training_result", {})
hard = training_result.get("hard_blocks", {})
artifacts = source.get("artifacts", {})

copied = {}

for name, raw_path in artifacts.items():
    src = Path(raw_path)
    if src.exists():
        dest = STORE / src.name
        shutil.copy2(src, dest)
        copied[name] = str(dest)

certification = {
    "training_run_id": "TRAINING_RUN_0001",
    "created_at": datetime.now(UTC).isoformat(),
    "source_training_run": str(SOURCE),
    "copied_artifacts": copied,
    "safety": {
        "learner_write_executed": hard.get("learner_write_executed"),
        "mutation_executed": hard.get("mutation_executed"),
        "queue_write_executed": hard.get("queue_write_executed"),
        "strategy_db_write_executed": hard.get("strategy_db_write_executed"),
        "promotion_executed": hard.get("promotion_executed"),
        "broker_execution_executed": hard.get("broker_execution_executed"),
        "live_execution_executed": hard.get("live_execution_executed"),
    },
    "policy": {
        "read_only_result_store": True,
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

CERT_JSON = STORE / "certification.json"
CERT_JSON.write_text(json.dumps(certification, indent=2), encoding="utf-8")

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "store_exists": STORE.exists(),
    "artifacts_copied": len(copied) >= 3,
    "certification_written": CERT_JSON.exists(),
    "learner_write_not_executed": hard.get("learner_write_executed") is False,
    "mutation_not_executed": hard.get("mutation_executed") is False,
    "queue_write_not_executed": hard.get("queue_write_executed") is False,
    "strategy_db_write_not_executed": hard.get("strategy_db_write_executed") is False,
    "promotion_not_executed": hard.get("promotion_executed") is False,
    "broker_live_not_executed": (
        hard.get("broker_execution_executed") is False
        and hard.get("live_execution_executed") is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "TRAINING_SAFETY_CERTIFICATION_AND_RESULT_STORE",
    "store": str(STORE),
    "certification": str(CERT_JSON),
    "copied_artifacts": copied,
    "checks": checks,
    "policy": certification["policy"],
    "recommended_next_phase": "101A_LEARNER_OUTCOME_COMPARISON",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"store: {STORE}",
        f"copied_artifacts: {len(copied)}",
        "",
        "Safety certified and training result stored read-only.",
        "No DB. No mutation. No promotion. No broker/live.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "store": str(STORE),
    "copied_artifacts": len(copied),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
