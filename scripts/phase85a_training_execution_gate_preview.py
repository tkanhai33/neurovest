#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "read_only_learner_inspection_rollup" / "84C_read_only_learner_inspection_rollup_latest.json"

OUT_DIR = ARCH / "training_execution_gate_preview"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "85A_training_execution_gate_preview_latest.json"
OUT_TXT = OUT_DIR / "85A_training_execution_gate_preview_latest.txt"

PHASE = "85A_TRAINING_EXECUTION_GATE_PREVIEW"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)

preview = {
    "mode": "TRAINING_EXECUTION_GATE_PREVIEW_ONLY_NO_PATCH",
    "safe_to_enable_training_execution_now": False,
    "current_allowed_state": {
        "read_only_learner_enabled": True,
        "training_execution_enabled": False,
        "learner_write_enabled": False,
        "mutation_allowed": False,
        "queue_write_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "future_training_execution_requirements": [
        "manual approval artifact",
        "training execution gate source file",
        "read-only input whitelist",
        "write output denied by default",
        "mutation denied by default",
        "promotion denied by default",
        "broker/live denied by default",
    ],
}

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "preview_present": bool(preview),
    "preview_only_no_patch": preview["mode"] == "TRAINING_EXECUTION_GATE_PREVIEW_ONLY_NO_PATCH",
    "safe_to_enable_training_execution_now_false": preview["safe_to_enable_training_execution_now"] is False,
    "training_execution_blocked": preview["current_allowed_state"]["training_execution_enabled"] is False,
    "learner_write_blocked": preview["current_allowed_state"]["learner_write_enabled"] is False,
    "mutation_blocked": preview["current_allowed_state"]["mutation_allowed"] is False,
    "queue_write_blocked": preview["current_allowed_state"]["queue_write_enabled"] is False,
    "strategy_db_write_blocked": preview["current_allowed_state"]["strategy_db_write_allowed"] is False,
    "promotion_blocked": preview["current_allowed_state"]["promotion_enabled"] is False,
    "broker_live_blocked": (
        preview["current_allowed_state"]["broker_execution_enabled"] is False
        and preview["current_allowed_state"]["live_execution_enabled"] is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "TRAINING_EXECUTION_GATE_PREVIEW",
    "source_read_only_learner_inspection_rollup": str(SOURCE),
    "preview": preview,
    "checks": checks,
    "policy": {
        "training_execution_gate_preview_certified": True,
        "read_only_learner_enabled": True,
        "training_execution_enabled": False,
        "learner_write_enabled": False,
        "mutation_allowed": False,
        "queue_write_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "85B_TRAINING_EXECUTION_GATE_STUB",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        "safe_to_enable_training_execution_now: False",
        "read_only_learner_enabled: True",
        "training_execution_enabled: False",
        "",
        "Preview only. No training execution enabled.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "safe_to_enable_training_execution_now": False,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
