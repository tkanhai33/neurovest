#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "training_unlock_decision_rollup" / "86A_training_unlock_decision_rollup_latest.json"

OUT_DIR = ARCH / "read_only_training_system_handoff"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "86B_read_only_training_system_handoff_latest.json"
OUT_TXT = OUT_DIR / "86B_read_only_training_system_handoff_latest.txt"

PHASE = "86B_READ_ONLY_TRAINING_SYSTEM_HANDOFF"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)

handoff = {
    "system_state": "READ_ONLY_LEARNER_ENABLED_TRAINING_EXECUTION_BLOCKED",
    "completed": [
        "real historical VFV.TO bar fixture certified",
        "stress report certified",
        "manual activation gate certified disabled",
        "near-miss queue certified capped at 3 disabled",
        "quarantine/trash path certified disabled",
        "read-only learner enabled",
        "read-only learner inspection certified",
        "training execution gate certified disabled",
        "training unlock decision says do not enable execution",
    ],
    "next_required_sequence": [
        "87A_MANUAL_APPROVAL_ARTIFACT",
        "88A_TRAINING_INPUT_WHITELIST",
        "89A_TRAINING_OUTPUT_SANDBOX",
        "90A_NO_MUTATION_TRAINING_DRY_RUN",
        "91A_NO_DB_NO_PROMOTION_NO_BROKER_CERTIFICATION",
        "92A_TRAINING_RESULT_READ_ONLY_STORE",
        "93A_ROLLBACK_RELOCK_GATE",
        "94A_FINAL_TRAINING_UNLOCK_DECISION",
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
    "handoff_present": bool(handoff),
    "training_execution_blocked": handoff["hard_blocks"]["training_execution_enabled"] is False,
    "learner_write_blocked": handoff["hard_blocks"]["learner_write_enabled"] is False,
    "mutation_blocked": handoff["hard_blocks"]["mutation_allowed"] is False,
    "queue_write_blocked": handoff["hard_blocks"]["queue_write_enabled"] is False,
    "strategy_db_write_blocked": handoff["hard_blocks"]["strategy_db_write_allowed"] is False,
    "promotion_blocked": handoff["hard_blocks"]["promotion_enabled"] is False,
    "broker_live_blocked": (
        handoff["hard_blocks"]["broker_execution_enabled"] is False
        and handoff["hard_blocks"]["live_execution_enabled"] is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "READ_ONLY_TRAINING_SYSTEM_HANDOFF",
    "source_unlock_decision": str(SOURCE),
    "handoff": handoff,
    "checks": checks,
    "policy": {
        "read_only_training_system_handoff_certified": True,
        **handoff["hard_blocks"],
    },
    "recommended_next_phase": "87A_MANUAL_APPROVAL_ARTIFACT",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"system_state: {handoff['system_state']}",
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
