#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "54A_qwen_read_only_handoff_export_summary_stub_latest.json"

PHASE = "54A_QWEN_READ_ONLY_HANDOFF_EXPORT_SUMMARY_STUB"

HANDOFF = SANDBOX / "53C_handoff_bundle_refresh_latest.json"

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

    export_summary = {
        "status": "qwen_read_only_handoff_export_summary_ready",
        "export_mode": "read_only_summary_export_only",

        "handoff_certified": handoff.get("certified") is True,

        "export_snapshot": {
            "stage": handoff.get("stage"),
            "latest_confirmed_phase": handoff.get(
                "latest_confirmed_phase"
            ),
            "current_capabilities": handoff.get(
                "current_capabilities",
                [],
            ),
            "still_disabled": handoff.get(
                "still_disabled",
                [],
            ),
            "critical_safety_locks": handoff.get(
                "critical_safety_locks",
                {},
            ),
            "next_recommended_phase": handoff.get(
                "next_recommended_phase"
            ),
        },

        "export_read_allowed": True,
        "export_write_allowed": False,

        "allowed_export_sections": [
            "architecture_state",
            "certified_capabilities",
            "disabled_capabilities",
            "safety_lock_state",
            "next_read_only_phase",
        ],

        "forbidden_export_actions": [
            "file_write",
            "implementation_patch",
            "shell_execution",
            "runtime_execution",
            "source_mutation",
            "strategy_enablement",
            "simulation_enablement",
            "learning_enablement",
            "promotion_enablement",
            "broker_execution",
            "live_execution",
            "recursive_self_execution",
            "autonomous_phase_execution",
        ],

        "actions_allowed": False,
        "writes_allowed": False,
        "runtime_allowed": False,
        "shell_execution_allowed": False,
        "source_mutation_allowed": False,
        "broker_or_live_allowed": False,
        "recursive_execution_allowed": False,
        "autonomous_phase_execution_allowed": False,

        "recommended_next_read_only_phase":
            "54B_QWEN_READ_ONLY_HANDOFF_EXPORT_SUMMARY_ROLLUP_CERTIFICATION",
    }

    result["export_summary_payload"] = export_summary

    result["checks"]["handoff_exists"] = HANDOFF.exists()

    result["checks"]["handoff_certified"] = (
        handoff.get("certified") is True
    )

    result["checks"]["status_ok"] = (
        export_summary["status"]
        == "qwen_read_only_handoff_export_summary_ready"
    )

    result["checks"]["export_mode_read_only"] = (
        export_summary["export_mode"]
        == "read_only_summary_export_only"
    )

    result["checks"]["snapshot_present"] = (
        len(export_summary["export_snapshot"]) > 0
    )

    result["checks"]["export_read_allowed"] = (
        export_summary["export_read_allowed"] is True
    )

    result["checks"]["export_write_blocked"] = (
        export_summary["export_write_allowed"] is False
    )

    result["checks"]["allowed_sections_present"] = (
        len(export_summary["allowed_export_sections"]) > 0
    )

    result["checks"]["forbidden_actions_present"] = (
        len(export_summary["forbidden_export_actions"]) > 0
    )

    result["checks"]["actions_not_allowed"] = (
        export_summary["actions_allowed"] is False
    )

    result["checks"]["writes_not_allowed"] = (
        export_summary["writes_allowed"] is False
    )

    result["checks"]["runtime_not_allowed"] = (
        export_summary["runtime_allowed"] is False
    )

    result["checks"]["shell_execution_not_allowed"] = (
        export_summary["shell_execution_allowed"] is False
    )

    result["checks"]["source_mutation_not_allowed"] = (
        export_summary["source_mutation_allowed"] is False
    )

    result["checks"]["broker_or_live_not_allowed"] = (
        export_summary["broker_or_live_allowed"] is False
    )

    result["checks"]["recursive_execution_not_allowed"] = (
        export_summary["recursive_execution_allowed"] is False
    )

    result["checks"]["autonomous_phase_execution_not_allowed"] = (
        export_summary["autonomous_phase_execution_allowed"] is False
    )

    result["checks"]["has_next_read_only_phase"] = bool(
        export_summary["recommended_next_read_only_phase"]
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
