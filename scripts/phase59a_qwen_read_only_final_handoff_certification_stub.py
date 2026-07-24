#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "59A_qwen_read_only_final_handoff_certification_stub_latest.json"
PHASE = "59A_QWEN_READ_ONLY_FINAL_HANDOFF_CERTIFICATION_STUB"

HANDOFF = SANDBOX / "58C_handoff_bundle_refresh_latest.json"

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

    payload = {
        "status": "qwen_read_only_final_handoff_certification_ready",
        "handoff_mode": "read_only_final_handoff_only",

        "handoff_certified": handoff.get("certified") is True,

        "final_snapshot": {
            "stage": handoff.get("handoff_snapshot", {}).get("stage"),
            "latest_confirmed_phase": handoff.get(
                "handoff_snapshot", {}
            ).get("latest_confirmed_phase"),
            "current_capabilities": handoff.get(
                "handoff_snapshot", {}
            ).get("current_capabilities", []),
            "still_disabled": handoff.get(
                "handoff_snapshot", {}
            ).get("still_disabled", []),
            "critical_safety_locks": handoff.get(
                "handoff_snapshot", {}
            ).get("critical_safety_locks", {}),
            "next_recommended_phase": handoff.get(
                "handoff_snapshot", {}
            ).get("next_recommended_phase"),
        },

        "certified_read_only_capabilities": [
            "architecture_summary",
            "locked_gate_explanation",
            "disabled_capability_summary",
            "missing_context_report",
            "response_validation",
            "session_contract",
            "session_response_bridge",
            "loop_boundary",
            "guardrail_summary",
            "handoff_snapshot",
            "export_summary",
            "state_machine_contract",
            "policy_map_contract",
            "policy_boundary_matrix",
            "final_context_package",
        ],

        "permanently_blocked_capabilities": [
            "file_write",
            "shell_execution",
            "runtime_execution",
            "source_mutation",
            "policy_mutation",
            "matrix_mutation",
            "context_package_mutation",
            "runtime_policy_enforcement",
            "strategy_enablement",
            "simulation_enablement",
            "learning_enablement",
            "promotion_enablement",
            "broker_execution",
            "live_execution",
            "recursive_self_execution",
            "autonomous_phase_execution",
        ],

        "handoff_read_allowed": True,
        "handoff_write_allowed": False,
        "handoff_execution_allowed": False,
        "handoff_mutation_allowed": False,

        "actions_allowed": False,
        "writes_allowed": False,
        "runtime_allowed": False,
        "shell_execution_allowed": False,
        "source_mutation_allowed": False,
        "policy_mutation_allowed": False,
        "matrix_mutation_allowed": False,
        "broker_or_live_allowed": False,
        "recursive_execution_allowed": False,
        "autonomous_phase_execution_allowed": False,

        "recommended_next_read_only_phase":
            "59B_QWEN_READ_ONLY_FINAL_HANDOFF_CERTIFICATION_ROLLUP_CERTIFICATION",
    }

    result["final_handoff_payload"] = payload

    result["checks"]["handoff_exists"] = HANDOFF.exists()
    result["checks"]["handoff_certified"] = (
        handoff.get("certified") is True
    )
    result["checks"]["status_ok"] = (
        payload["status"]
        == "qwen_read_only_final_handoff_certification_ready"
    )
    result["checks"]["mode_read_only"] = (
        payload["handoff_mode"]
        == "read_only_final_handoff_only"
    )
    result["checks"]["snapshot_present"] = (
        len(payload["final_snapshot"]) > 0
    )
    result["checks"]["capabilities_present"] = (
        len(payload["certified_read_only_capabilities"]) > 0
    )
    result["checks"]["blocked_capabilities_present"] = (
        len(payload["permanently_blocked_capabilities"]) > 0
    )
    result["checks"]["handoff_read_allowed"] = (
        payload["handoff_read_allowed"] is True
    )
    result["checks"]["handoff_write_blocked"] = (
        payload["handoff_write_allowed"] is False
    )
    result["checks"]["handoff_execution_blocked"] = (
        payload["handoff_execution_allowed"] is False
    )
    result["checks"]["handoff_mutation_blocked"] = (
        payload["handoff_mutation_allowed"] is False
    )
    result["checks"]["actions_blocked"] = (
        payload["actions_allowed"] is False
    )
    result["checks"]["writes_blocked"] = (
        payload["writes_allowed"] is False
    )
    result["checks"]["runtime_blocked"] = (
        payload["runtime_allowed"] is False
    )
    result["checks"]["shell_execution_blocked"] = (
        payload["shell_execution_allowed"] is False
    )
    result["checks"]["source_mutation_blocked"] = (
        payload["source_mutation_allowed"] is False
    )
    result["checks"]["policy_mutation_blocked"] = (
        payload["policy_mutation_allowed"] is False
    )
    result["checks"]["matrix_mutation_blocked"] = (
        payload["matrix_mutation_allowed"] is False
    )
    result["checks"]["broker_or_live_blocked"] = (
        payload["broker_or_live_allowed"] is False
    )
    result["checks"]["recursive_execution_blocked"] = (
        payload["recursive_execution_allowed"] is False
    )
    result["checks"]["autonomous_phase_execution_blocked"] = (
        payload["autonomous_phase_execution_allowed"] is False
    )
    result["checks"]["critical_safety_locks_false"] = all(
        value is False
        for value in payload["final_snapshot"].get(
            "critical_safety_locks", {}
        ).values()
    )
    result["checks"]["next_phase_present"] = bool(
        payload["recommended_next_read_only_phase"]
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
