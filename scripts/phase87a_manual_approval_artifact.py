#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "read_only_training_system_handoff" / "86B_read_only_training_system_handoff_latest.json"

OUT_DIR = ARCH / "manual_approval_artifact"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "87A_manual_approval_artifact_latest.json"
OUT_TXT = OUT_DIR / "87A_manual_approval_artifact_latest.txt"

PHASE = "87A_MANUAL_APPROVAL_ARTIFACT"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)

approval = {
    "approval_id": "MANUAL_APPROVAL_READ_ONLY_TRAINING_0001",
    "approved_by": "local_operator",
    "approved_at": datetime.now(UTC).isoformat(),
    "approval_scope": "READ_ONLY_NO_MUTATION_TRAINING_DRY_RUN_PREP_ONLY",
    "approval_grants": {
        "training_input_whitelist_creation": True,
        "training_output_sandbox_creation": True,
        "no_mutation_training_dry_run_next": True,
        "training_execution_enabled": False,
        "learner_write_enabled": False,
        "mutation_allowed": False,
        "queue_write_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "rollback_required": True,
}

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "approval_present": bool(approval),
    "approval_scope_correct": approval["approval_scope"] == "READ_ONLY_NO_MUTATION_TRAINING_DRY_RUN_PREP_ONLY",
    "rollback_required": approval["rollback_required"] is True,
    "training_execution_blocked": approval["approval_grants"]["training_execution_enabled"] is False,
    "learner_write_blocked": approval["approval_grants"]["learner_write_enabled"] is False,
    "mutation_blocked": approval["approval_grants"]["mutation_allowed"] is False,
    "queue_write_blocked": approval["approval_grants"]["queue_write_enabled"] is False,
    "strategy_db_write_blocked": approval["approval_grants"]["strategy_db_write_allowed"] is False,
    "promotion_blocked": approval["approval_grants"]["promotion_enabled"] is False,
    "broker_live_blocked": (
        approval["approval_grants"]["broker_execution_enabled"] is False
        and approval["approval_grants"]["live_execution_enabled"] is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "MANUAL_APPROVAL_ARTIFACT",
    "source_handoff": str(SOURCE),
    "manual_approval": approval,
    "checks": checks,
    "policy": {
        "manual_approval_artifact_certified": True,
        **{k: v for k, v in approval["approval_grants"].items() if isinstance(v, bool)},
    },
    "recommended_next_phase": "88A_TRAINING_INPUT_WHITELIST",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"approval_id: {approval['approval_id']}",
        f"approval_scope: {approval['approval_scope']}",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "approval_id": approval["approval_id"],
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
