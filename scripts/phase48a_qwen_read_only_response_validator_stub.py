#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "48A_qwen_read_only_response_validator_stub_latest.json"

PHASE = "48A_QWEN_READ_ONLY_RESPONSE_VALIDATOR_STUB"

HANDOFF = SANDBOX / "47C_handoff_bundle_refresh_latest.json"

ALLOWED_RESPONSE_TYPES = {
    "architecture_summary",
    "locked_gate_explanation",
    "disabled_capability_summary",
    "missing_context_report",
    "read_only_next_phase_recommendation",
}

FORBIDDEN_RESPONSE_TYPES = {
    "implementation_patch",
    "file_write_instruction",
    "shell_execution_instruction",
    "runtime_execution_instruction",
    "source_mutation_instruction",
    "strategy_enablement_instruction",
    "simulation_enablement_instruction",
    "learning_instruction",
    "promotion_instruction",
    "broker_execution_instruction",
    "live_execution_instruction",
}

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

    sample_allowed_responses = [
        {
            "type": "architecture_summary",
            "text": "Summarize the certified architecture stage.",
            "allowed": True,
        },
        {
            "type": "locked_gate_explanation",
            "text": "Explain why disabled capabilities remain locked.",
            "allowed": True,
        },
        {
            "type": "missing_context_report",
            "text": "Report missing context without requesting changes.",
            "allowed": True,
        },
        {
            "type": "read_only_next_phase_recommendation",
            "text": handoff.get("next_recommended_phase"),
            "allowed": True,
        },
    ]

    sample_blocked_responses = [
        {
            "type": "implementation_patch",
            "text": "Generate source changes.",
            "allowed": False,
        },
        {
            "type": "runtime_execution_instruction",
            "text": "Execute runtime systems.",
            "allowed": False,
        },
        {
            "type": "broker_execution_instruction",
            "text": "Place broker orders.",
            "allowed": False,
        },
        {
            "type": "live_execution_instruction",
            "text": "Enable live trading.",
            "allowed": False,
        },
    ]

    validator_payload = {
        "status": "qwen_read_only_response_validator_ready",
        "validator_mode": "read_only_response_validation_only",

        "allowed_response_types": sorted(
            ALLOWED_RESPONSE_TYPES
        ),

        "forbidden_response_types": sorted(
            FORBIDDEN_RESPONSE_TYPES
        ),

        "sample_allowed_responses": sample_allowed_responses,

        "sample_blocked_responses": sample_blocked_responses,

        "response_validation_allowed": True,

        "actions_allowed": False,
        "writes_allowed": False,
        "runtime_allowed": False,
        "source_mutation_allowed": False,
        "broker_or_live_allowed": False,

        "recommended_next_read_only_phase":
            "48B_QWEN_READ_ONLY_RESPONSE_VALIDATOR_ROLLUP_CERTIFICATION",
    }

    result["validator_payload"] = validator_payload

    result["checks"]["handoff_exists"] = HANDOFF.exists()
    result["checks"]["handoff_certified"] = handoff.get("certified") is True

    result["checks"]["status_ok"] = (
        validator_payload["status"]
        == "qwen_read_only_response_validator_ready"
    )

    result["checks"]["validator_mode_read_only"] = (
        validator_payload["validator_mode"]
        == "read_only_response_validation_only"
    )

    result["checks"]["allowed_types_present"] = (
        len(validator_payload["allowed_response_types"]) > 0
    )

    result["checks"]["forbidden_types_present"] = (
        len(validator_payload["forbidden_response_types"]) > 0
    )

    result["checks"]["allowed_samples_pass"] = all(
        item.get("allowed") is True
        for item in sample_allowed_responses
    )

    result["checks"]["blocked_samples_rejected"] = all(
        item.get("allowed") is False
        for item in sample_blocked_responses
    )

    result["checks"]["response_validation_allowed"] = (
        validator_payload["response_validation_allowed"] is True
    )

    result["checks"]["actions_not_allowed"] = (
        validator_payload["actions_allowed"] is False
    )

    result["checks"]["writes_not_allowed"] = (
        validator_payload["writes_allowed"] is False
    )

    result["checks"]["runtime_not_allowed"] = (
        validator_payload["runtime_allowed"] is False
    )

    result["checks"]["source_mutation_not_allowed"] = (
        validator_payload["source_mutation_allowed"] is False
    )

    result["checks"]["broker_or_live_not_allowed"] = (
        validator_payload["broker_or_live_allowed"] is False
    )

    result["checks"]["has_next_read_only_phase"] = bool(
        validator_payload["recommended_next_read_only_phase"]
    )

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })


OUT.write_text(
    json.dumps(result, indent=2),
    encoding="utf-8"
)

print(json.dumps(result, indent=2))
print(f"\nWROTE: {OUT}")
