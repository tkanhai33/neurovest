#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "53A_qwen_read_only_handoff_freeze_stub_latest.json"
PHASE = "53A_QWEN_READ_ONLY_HANDOFF_FREEZE_STUB"

HANDOFF = SANDBOX / "52C_handoff_bundle_refresh_latest.json"

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "handoff_source": str(HANDOFF),
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    handoff = (
        json.loads(HANDOFF.read_text(encoding="utf-8"))
        if HANDOFF.exists()
        else {}
    )

    freeze_payload = {
        "status": "qwen_read_only_handoff_freeze_ready",
        "freeze_mode": "read_only_handoff_snapshot_only",

        "handoff_certified": handoff.get("certified") is True,

        "snapshot_fields": {
            "stage": handoff.get("stage"),
            "latest_confirmed_phase": handoff.get("latest_confirmed_phase"),
            "current_capabilities": handoff.get("current_capabilities", []),
            "still_disabled": handoff.get("still_disabled", []),
            "critical_safety_locks": handoff.get("critical_safety_locks", {}),
            "next_recommended_phase": handoff.get("next_recommended_phase"),
        },

        "snapshot_read_allowed": True,
        "snapshot_write_allowed": False,

        "actions_allowed": False,
        "writes_allowed": False,
        "runtime_allowed": False,
        "shell_execution_allowed": False,
        "source_mutation_allowed": False,
        "broker_or_live_allowed": False,
        "recursive_execution_allowed": False,
        "autonomous_phase_execution_allowed": False,

        "recommended_next_read_only_phase":
            "53B_QWEN_READ_ONLY_HANDOFF_FREEZE_ROLLUP_CERTIFICATION",
    }

    result["freeze_payload"] = freeze_payload

    result["checks"]["handoff_exists"] = HANDOFF.exists()
    result["checks"]["handoff_certified"] = (
        handoff.get("certified") is True
    )

    result["checks"]["status_ok"] = (
        freeze_payload["status"]
        == "qwen_read_only_handoff_freeze_ready"
    )

    result["checks"]["freeze_mode_read_only"] = (
        freeze_payload["freeze_mode"]
        == "read_only_handoff_snapshot_only"
    )

    result["checks"]["snapshot_fields_present"] = (
        len(freeze_payload["snapshot_fields"]) > 0
    )

    result["checks"]["snapshot_read_allowed"] = (
        freeze_payload["snapshot_read_allowed"] is True
    )

    result["checks"]["snapshot_write_blocked"] = (
        freeze_payload["snapshot_write_allowed"] is False
    )

    result["checks"]["actions_not_allowed"] = (
        freeze_payload["actions_allowed"] is False
    )

    result["checks"]["writes_not_allowed"] = (
        freeze_payload["writes_allowed"] is False
    )

    result["checks"]["runtime_not_allowed"] = (
        freeze_payload["runtime_allowed"] is False
    )

    result["checks"]["shell_execution_not_allowed"] = (
        freeze_payload["shell_execution_allowed"] is False
    )

    result["checks"]["source_mutation_not_allowed"] = (
        freeze_payload["source_mutation_allowed"] is False
    )

    result["checks"]["broker_or_live_not_allowed"] = (
        freeze_payload["broker_or_live_allowed"] is False
    )

    result["checks"]["recursive_execution_not_allowed"] = (
        freeze_payload["recursive_execution_allowed"] is False
    )

    result["checks"]["autonomous_phase_execution_not_allowed"] = (
        freeze_payload["autonomous_phase_execution_allowed"] is False
    )

    result["checks"]["has_next_read_only_phase"] = bool(
        freeze_payload["recommended_next_read_only_phase"]
    )

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(
    json.dumps(result, indent=2),
    encoding="utf-8",
)

print(json.dumps(result, indent=2))
print(f"\nWROTE: {OUT}")
