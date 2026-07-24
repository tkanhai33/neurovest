#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "read_only_learner_enablement_preview" / "83D_read_only_learner_enablement_preview_latest.json"
TARGET = ROOT / "backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/training_read_only_learner.py"

OUT_DIR = ARCH / "learner_enablement_patch_preview_only"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "83E_learner_enablement_patch_preview_only_latest.json"
OUT_TXT = OUT_DIR / "83E_learner_enablement_patch_preview_only_latest.txt"

PHASE = "83E_LEARNER_ENABLEMENT_PATCH_PREVIEW_ONLY"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)
target_text = TARGET.read_text(encoding="utf-8") if TARGET.exists() else ""

patch_preview = {
    "mode": "PATCH_PREVIEW_ONLY_NO_WRITE",
    "target_file": str(TARGET),
    "planned_change": {
        "from": "READ_ONLY_LEARNER_ENABLED = False",
        "to": "READ_ONLY_LEARNER_ENABLED = True",
    },
    "must_remain_false": [
        "TRAINING_ENABLED",
        "LEARNER_WRITE_ENABLED",
        "MUTATION_ALLOWED",
        "QUEUE_WRITE_ENABLED",
        "STRATEGY_DB_WRITE_ALLOWED",
        "PROMOTION_ENABLED",
        "BROKER_EXECUTION_ENABLED",
        "LIVE_EXECUTION_ENABLED",
    ],
    "purpose": "preview enabling read-only learner inspection only",
}

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "target_exists": TARGET.exists(),
    "target_currently_read_only_learner_disabled": "READ_ONLY_LEARNER_ENABLED = False" in target_text,
    "preview_only_no_write": patch_preview["mode"] == "PATCH_PREVIEW_ONLY_NO_WRITE",
    "training_still_blocked": "TRAINING_ENABLED = False" in target_text,
    "learner_write_still_blocked": "LEARNER_WRITE_ENABLED = False" in target_text,
    "mutation_still_blocked": "MUTATION_ALLOWED = False" in target_text,
    "queue_write_still_blocked": "QUEUE_WRITE_ENABLED = False" in target_text,
    "strategy_db_write_still_blocked": "STRATEGY_DB_WRITE_ALLOWED = False" in target_text,
    "promotion_still_blocked": "PROMOTION_ENABLED = False" in target_text,
    "broker_live_still_blocked": (
        "BROKER_EXECUTION_ENABLED = False" in target_text
        and "LIVE_EXECUTION_ENABLED = False" in target_text
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "LEARNER_ENABLEMENT_PATCH_PREVIEW_ONLY",
    "source_enablement_preview": str(SOURCE),
    "patch_preview": patch_preview,
    "checks": checks,
    "policy": {
        "patch_preview_certified": True,
        "patch_apply_allowed_now": False,
        "training_enabled": False,
        "learner_write_enabled": False,
        "mutation_allowed": False,
        "queue_write_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "83F_READ_ONLY_LEARNER_ENABLEMENT_PATCH_APPLY",
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
        "- READ_ONLY_LEARNER_ENABLED False -> True",
        "- TRAINING_ENABLED remains False",
        "- LEARNER_WRITE_ENABLED remains False",
        "- mutation/queue/db/promotion/broker/live remain False",
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
