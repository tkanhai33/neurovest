#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "dev_command_read_only_execution_rollup" / "108D_dev_command_read_only_execution_rollup_latest.json"
EXECUTOR = ROOT / "backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/dev_command_read_only_executor.py"

OUT_DIR = ARCH / "dev_command_execution_enablement_preview"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "109A_dev_command_execution_enablement_preview_latest.json"
OUT_TXT = OUT_DIR / "109A_dev_command_execution_enablement_preview_latest.txt"

PHASE = "109A_DEV_COMMAND_EXECUTION_ENABLEMENT_PREVIEW"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)
executor_text = EXECUTOR.read_text(encoding="utf-8") if EXECUTOR.exists() else ""

preview = {
    "mode": "DEV_COMMAND_EXECUTION_ENABLEMENT_PREVIEW_ONLY_NO_PATCH",
    "target_executor": str(EXECUTOR),
    "planned_change": {
        "from": "COMMAND_EXECUTION_ENABLED = False",
        "to": "COMMAND_EXECUTION_ENABLED = True",
    },
    "activation_scope": "READ_ONLY_DEV_COMMAND_PREVIEW_EXECUTION_ONLY",
    "allowed_after_apply": [
        "preview_dev_command",
        "return command intent",
        "return doctrine/safety blocks",
    ],
    "still_blocked": {
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
    "executor_exists": EXECUTOR.exists(),
    "executor_currently_command_execution_disabled": "COMMAND_EXECUTION_ENABLED = False" in executor_text,
    "preview_only_no_patch": preview["mode"] == "DEV_COMMAND_EXECUTION_ENABLEMENT_PREVIEW_ONLY_NO_PATCH",
    "training_still_blocked": preview["still_blocked"]["training_execution_enabled"] is False,
    "learner_write_still_blocked": preview["still_blocked"]["learner_write_enabled"] is False,
    "mutation_still_blocked": preview["still_blocked"]["mutation_allowed"] is False,
    "queue_write_still_blocked": preview["still_blocked"]["queue_write_enabled"] is False,
    "strategy_db_write_still_blocked": preview["still_blocked"]["strategy_db_write_allowed"] is False,
    "promotion_still_blocked": preview["still_blocked"]["promotion_enabled"] is False,
    "broker_live_still_blocked": (
        preview["still_blocked"]["broker_execution_enabled"] is False
        and preview["still_blocked"]["live_execution_enabled"] is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "DEV_COMMAND_EXECUTION_ENABLEMENT_PREVIEW",
    "source_read_only_rollup": str(SOURCE),
    "preview": preview,
    "checks": checks,
    "policy": {
        "dev_command_execution_enablement_preview_certified": True,
        "patch_apply_allowed_now": False,
        "command_execution_enabled": False,
        "read_only_preview_enabled": True,
        **preview["still_blocked"],
    },
    "recommended_next_phase": "109B_DEV_COMMAND_EXECUTION_ENABLEMENT_PATCH_APPLY",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        "patch_apply_allowed_now: False",
        "",
        "Preview only:",
        "- COMMAND_EXECUTION_ENABLED False -> True",
        "- Scope remains read-only preview execution only",
        "- Training/db/mutation/promotion/broker/live remain False",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "patch_apply_allowed_now": False,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
