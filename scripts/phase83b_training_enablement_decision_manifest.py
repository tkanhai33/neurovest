#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "training_enablement_final_safety_rollup" / "83A_training_enablement_final_safety_rollup_latest.json"

OUT_DIR = ARCH / "training_enablement_decision_manifest"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "83B_training_enablement_decision_manifest_latest.json"
OUT_TXT = OUT_DIR / "83B_training_enablement_decision_manifest_latest.txt"

PHASE = "83B_TRAINING_ENABLEMENT_DECISION_MANIFEST"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)

decision_manifest = {
    "mode": "DECISION_MANIFEST_ONLY_NO_ENABLEMENT",
    "decision": "DO_NOT_ENABLE_TRAINING_YET",
    "safe_to_enable_training_now": False,
    "reason": [
        "learner is certified disabled/read-only only",
        "manual activation is still disabled",
        "queue writes are still disabled",
        "mutation is still disabled",
        "strategy DB writes are still disabled",
        "promotion is still disabled",
        "broker/live remains disabled",
    ],
    "next_unlock_steps": [
        "83C_MANUAL_APPROVAL_GATE_PREVIEW",
        "83D_READ_ONLY_LEARNER_ENABLEMENT_PREVIEW",
        "83E_LEARNER_ENABLEMENT_PATCH_PREVIEW_ONLY",
    ],
}

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "manifest_present": bool(decision_manifest),
    "decision_blocks_training": decision_manifest["decision"] == "DO_NOT_ENABLE_TRAINING_YET",
    "safe_to_enable_training_now_false": decision_manifest["safe_to_enable_training_now"] is False,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "TRAINING_ENABLEMENT_DECISION_MANIFEST",
    "source_final_safety_rollup": str(SOURCE),
    "decision_manifest": decision_manifest,
    "checks": checks,
    "policy": {
        "training_enablement_decision_manifest_certified": True,
        "training_enabled": False,
        "learner_write_enabled": False,
        "mutation_allowed": False,
        "queue_write_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "83C_MANUAL_APPROVAL_GATE_PREVIEW",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"decision: {decision_manifest['decision']}",
        "safe_to_enable_training_now: False",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "decision": decision_manifest["decision"],
    "safe_to_enable_training_now": False,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
