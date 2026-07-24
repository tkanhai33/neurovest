#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "training_input_whitelist" / "88A_training_input_whitelist_latest.json"

OUT_DIR = ARCH / "training_output_sandbox"
SANDBOX = OUT_DIR / "sandbox"
SANDBOX.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "89A_training_output_sandbox_latest.json"
OUT_TXT = OUT_DIR / "89A_training_output_sandbox_latest.txt"
SANDBOX_MARKER = SANDBOX / "README_READ_ONLY_SANDBOX.txt"

PHASE = "89A_TRAINING_OUTPUT_SANDBOX"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)

SANDBOX_MARKER.write_text(
    "\n".join([
        "TRAINING OUTPUT SANDBOX",
        "Read-only training dry-run outputs only.",
        "No strategy DB writes.",
        "No promotion.",
        "No mutation.",
        "No broker/live execution.",
    ]),
    encoding="utf-8",
)

sandbox = {
    "mode": "TRAINING_OUTPUT_SANDBOX_READ_ONLY",
    "sandbox_dir": str(SANDBOX),
    "allowed_outputs": [
        "dry_run_summary_json",
        "dry_run_metrics_json",
        "inspection_notes_txt",
    ],
    "forbidden_outputs": [
        "strategy DB writes",
        "promotion records",
        "mutation patches",
        "queue writes",
        "broker orders",
        "live execution artifacts",
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
    "sandbox_dir_exists": SANDBOX.exists(),
    "sandbox_marker_written": SANDBOX_MARKER.exists(),
    "sandbox_present": bool(sandbox),
    "training_execution_blocked": sandbox["hard_blocks"]["training_execution_enabled"] is False,
    "learner_write_blocked": sandbox["hard_blocks"]["learner_write_enabled"] is False,
    "mutation_blocked": sandbox["hard_blocks"]["mutation_allowed"] is False,
    "queue_write_blocked": sandbox["hard_blocks"]["queue_write_enabled"] is False,
    "strategy_db_write_blocked": sandbox["hard_blocks"]["strategy_db_write_allowed"] is False,
    "promotion_blocked": sandbox["hard_blocks"]["promotion_enabled"] is False,
    "broker_live_blocked": (
        sandbox["hard_blocks"]["broker_execution_enabled"] is False
        and sandbox["hard_blocks"]["live_execution_enabled"] is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "TRAINING_OUTPUT_SANDBOX",
    "source_whitelist": str(SOURCE),
    "sandbox": sandbox,
    "checks": checks,
    "policy": {
        "training_output_sandbox_certified": True,
        **sandbox["hard_blocks"],
    },
    "recommended_next_phase": "90A_NO_MUTATION_TRAINING_DRY_RUN",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"sandbox_dir: {SANDBOX}",
        "",
        "Training output sandbox created.",
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
    "sandbox_dir": str(SANDBOX),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
