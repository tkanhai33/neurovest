#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "training_enablement_decision_manifest" / "83B_training_enablement_decision_manifest_latest.json"

OUT_DIR = ARCH / "manual_approval_gate_preview"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "83C_manual_approval_gate_preview_latest.json"
OUT_TXT = OUT_DIR / "83C_manual_approval_gate_preview_latest.txt"

PHASE = "83C_MANUAL_APPROVAL_GATE_PREVIEW"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)

preview = {
    "mode": "MANUAL_APPROVAL_GATE_PREVIEW_ONLY_NO_PATCH",
    "approval_required": True,
    "safe_to_enable_training_now": False,
    "future_manual_approval_fields": [
        "approved_by",
        "approved_at",
        "approval_reason",
        "scope",
        "training_mode",
        "rollback_required",
    ],
    "allowed_future_scope": {
        "training_mode": "READ_ONLY_LEARNER_ONLY",
        "learner_write_enabled": False,
        "mutation_allowed": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "forbidden_now": [
        "enable training",
        "enable learner writes",
        "enable mutation",
        "enable queue writes",
        "write strategy DB",
        "promote candidate",
        "broker execution",
        "live execution",
    ],
}

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "preview_present": bool(preview),
    "preview_only_no_patch": preview["mode"] == "MANUAL_APPROVAL_GATE_PREVIEW_ONLY_NO_PATCH",
    "approval_required": preview["approval_required"] is True,
    "safe_to_enable_training_now_false": preview["safe_to_enable_training_now"] is False,
    "learner_write_blocked": preview["allowed_future_scope"]["learner_write_enabled"] is False,
    "mutation_blocked": preview["allowed_future_scope"]["mutation_allowed"] is False,
    "strategy_db_write_blocked": preview["allowed_future_scope"]["strategy_db_write_allowed"] is False,
    "promotion_blocked": preview["allowed_future_scope"]["promotion_enabled"] is False,
    "broker_live_blocked": (
        preview["allowed_future_scope"]["broker_execution_enabled"] is False
        and preview["allowed_future_scope"]["live_execution_enabled"] is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "MANUAL_APPROVAL_GATE_PREVIEW",
    "source_decision_manifest": str(SOURCE),
    "preview": preview,
    "checks": checks,
    "policy": {
        "manual_approval_gate_preview_certified": True,
        "training_enabled": False,
        "learner_write_enabled": False,
        "mutation_allowed": False,
        "queue_write_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "83D_READ_ONLY_LEARNER_ENABLEMENT_PREVIEW",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        "approval_required: True",
        "safe_to_enable_training_now: False",
        "",
        "Preview only. No training enabled.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "approval_required": True,
    "safe_to_enable_training_now": False,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
