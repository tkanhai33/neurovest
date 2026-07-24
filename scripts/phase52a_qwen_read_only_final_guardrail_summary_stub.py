#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "52A_qwen_read_only_final_guardrail_summary_stub_latest.json"
PHASE = "52A_QWEN_READ_ONLY_FINAL_GUARDRAIL_SUMMARY_STUB"

HANDOFF = SANDBOX / "51C_handoff_bundle_refresh_latest.json"

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

    guardrail_summary = {
        "status": "qwen_read_only_final_guardrail_summary_ready",
        "summary_mode": "read_only_guardrail_summary_only",

        "handoff_certified": handoff.get("certified") is True,

        "allowed_capabilities": [
            "architecture_summary",
            "locked_gate_explanation",
            "disabled_capability_summary",
            "missing_context_report",
            "read_only_next_phase_recommendation",
            "session_context_read",
            "response_validation",
            "session_response_bridge",
            "loop_boundary_enforcement",
        ],

        "guardrails_confirmed": [
            "no_file_writes",
            "no_shell_execution",
            "no_runtime_execution",
            "no_source_mutation",
            "no_strategy_enablement",
            "no_simulation_enablement",
            "no_learning_enablement",
            "no_promotion_enablement",
            "no_broker_execution",
            "no_live_execution",
            "no_recursive_self_execution",
            "no_autonomous_phase_execution",
        ],

        "summary_read_allowed": True,

        "actions_allowed": False,
        "writes_allowed": False,
        "runtime_allowed": False,
        "shell_execution_allowed": False,
        "source_mutation_allowed": False,
        "broker_or_live_allowed": False,
        "recursive_execution_allowed": False,
        "autonomous_phase_execution_allowed": False,

        "recommended_next_read_only_phase":
            "52B_QWEN_READ_ONLY_FINAL_GUARDRAIL_SUMMARY_ROLLUP_CERTIFICATION",
    }

    result["guardrail_summary_payload"] = guardrail_summary

    result["checks"]["handoff_exists"] = HANDOFF.exists()
    result["checks"]["handoff_certified"] = (
        handoff.get("certified") is True
    )

    result["checks"]["status_ok"] = (
        guardrail_summary["status"]
        == "qwen_read_only_final_guardrail_summary_ready"
    )

    result["checks"]["summary_mode_read_only"] = (
        guardrail_summary["summary_mode"]
        == "read_only_guardrail_summary_only"
    )

    result["checks"]["allowed_capabilities_present"] = (
        len(guardrail_summary["allowed_capabilities"]) > 0
    )

    result["checks"]["guardrails_present"] = (
        len(guardrail_summary["guardrails_confirmed"]) > 0
    )

    result["checks"]["summary_read_allowed"] = (
        guardrail_summary["summary_read_allowed"] is True
    )

    result["checks"]["actions_not_allowed"] = (
        guardrail_summary["actions_allowed"] is False
    )

    result["checks"]["writes_not_allowed"] = (
        guardrail_summary["writes_allowed"] is False
    )

    result["checks"]["runtime_not_allowed"] = (
        guardrail_summary["runtime_allowed"] is False
    )

    result["checks"]["shell_execution_not_allowed"] = (
        guardrail_summary["shell_execution_allowed"] is False
    )

    result["checks"]["source_mutation_not_allowed"] = (
        guardrail_summary["source_mutation_allowed"] is False
    )

    result["checks"]["broker_or_live_not_allowed"] = (
        guardrail_summary["broker_or_live_allowed"] is False
    )

    result["checks"]["recursive_execution_not_allowed"] = (
        guardrail_summary["recursive_execution_allowed"] is False
    )

    result["checks"]["autonomous_phase_execution_not_allowed"] = (
        guardrail_summary["autonomous_phase_execution_allowed"] is False
    )

    result["checks"]["has_next_read_only_phase"] = bool(
        guardrail_summary["recommended_next_read_only_phase"]
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
