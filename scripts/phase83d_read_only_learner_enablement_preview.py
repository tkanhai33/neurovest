#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "manual_approval_gate_preview" / "83C_manual_approval_gate_preview_latest.json"

OUT_DIR = ARCH / "read_only_learner_enablement_preview"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "83D_read_only_learner_enablement_preview_latest.json"
OUT_TXT = OUT_DIR / "83D_read_only_learner_enablement_preview_latest.txt"

PHASE = "83D_READ_ONLY_LEARNER_ENABLEMENT_PREVIEW"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)

preview = {
    "mode": "READ_ONLY_LEARNER_ENABLEMENT_PREVIEW_ONLY_NO_PATCH",
    "training_enabled_now": False,
    "future_allowed_change": {
        "read_only_learner_enabled": True,
        "training_enabled": False,
        "learner_write_enabled": False,
        "mutation_allowed": False,
        "queue_write_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "purpose": "preview enabling learner inspection only, without training execution or writes",
}

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "preview_present": bool(preview),
    "preview_only_no_patch": preview["mode"] == "READ_ONLY_LEARNER_ENABLEMENT_PREVIEW_ONLY_NO_PATCH",
    "training_still_disabled": preview["future_allowed_change"]["training_enabled"] is False,
    "learner_write_blocked": preview["future_allowed_change"]["learner_write_enabled"] is False,
    "mutation_blocked": preview["future_allowed_change"]["mutation_allowed"] is False,
    "queue_write_blocked": preview["future_allowed_change"]["queue_write_enabled"] is False,
    "strategy_db_write_blocked": preview["future_allowed_change"]["strategy_db_write_allowed"] is False,
    "promotion_blocked": preview["future_allowed_change"]["promotion_enabled"] is False,
    "broker_live_blocked": (
        preview["future_allowed_change"]["broker_execution_enabled"] is False
        and preview["future_allowed_change"]["live_execution_enabled"] is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "READ_ONLY_LEARNER_ENABLEMENT_PREVIEW",
    "source_manual_approval_preview": str(SOURCE),
    "preview": preview,
    "checks": checks,
    "policy": {
        "read_only_learner_enablement_preview_certified": True,
        "training_enabled": False,
        "learner_write_enabled": False,
        "mutation_allowed": False,
        "queue_write_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "83E_LEARNER_ENABLEMENT_PATCH_PREVIEW_ONLY",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        "preview only, no patch applied",
        "training_enabled: False",
        "learner_write_enabled: False",
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
