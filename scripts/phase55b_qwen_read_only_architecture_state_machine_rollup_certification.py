#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "55B_qwen_read_only_architecture_state_machine_rollup_certification_latest.json"

PHASE = "55B_QWEN_READ_ONLY_ARCHITECTURE_STATE_MACHINE_ROLLUP_CERTIFICATION"

ARTIFACT = SANDBOX / "55A_qwen_read_only_architecture_state_machine_stub_latest.json"

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "artifact": str(ARTIFACT),
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    data = (
        json.loads(ARTIFACT.read_text(encoding="utf-8"))
        if ARTIFACT.exists()
        else {}
    )

    state_machine = (
        data.get("state_machine_payload", {})
        if isinstance(data.get("state_machine_payload"), dict)
        else {}
    )

    result["source_phase"] = data.get("phase")
    result["source_certified"] = data.get("certified") is True

    result["state_machine_summary"] = {
        "status": state_machine.get("status"),
        "state_machine_mode": state_machine.get(
            "state_machine_mode"
        ),
        "states": state_machine.get(
            "states",
            [],
        ),
        "allowed_transitions": state_machine.get(
            "allowed_transitions",
            [],
        ),
        "forbidden_transitions": state_machine.get(
            "forbidden_transitions",
            [],
        ),
        "recommended_next_read_only_phase": state_machine.get(
            "recommended_next_read_only_phase"
        ),
    }

    result["checks"]["artifact_exists"] = ARTIFACT.exists()

    result["checks"]["source_certified"] = (
        data.get("certified") is True
    )

    result["checks"]["status_ok"] = (
        state_machine.get("status")
        == "qwen_read_only_architecture_state_machine_ready"
    )

    result["checks"]["mode_read_only"] = (
        state_machine.get("state_machine_mode")
        == "read_only_contract_only"
    )

    result["checks"]["states_present"] = (
        len(state_machine.get("states", [])) > 0
    )

    result["checks"]["allowed_transitions_present"] = (
        len(state_machine.get("allowed_transitions", [])) > 0
    )

    result["checks"]["forbidden_transitions_present"] = (
        len(state_machine.get("forbidden_transitions", [])) > 0
    )

    result["checks"]["handoff_certified"] = (
        state_machine.get("handoff_certified") is True
    )

    result["checks"]["read_allowed"] = (
        state_machine.get("read_allowed") is True
    )

    result["checks"]["summary_allowed"] = (
        state_machine.get("summary_allowed") is True
    )

    result["checks"]["recommendation_allowed"] = (
        state_machine.get("recommendation_allowed") is True
    )

    result["checks"]["actions_not_allowed"] = (
        state_machine.get("actions_allowed") is False
    )

    result["checks"]["writes_not_allowed"] = (
        state_machine.get("writes_allowed") is False
    )

    result["checks"]["runtime_not_allowed"] = (
        state_machine.get("runtime_allowed") is False
    )

    result["checks"]["shell_execution_not_allowed"] = (
        state_machine.get("shell_execution_allowed") is False
    )

    result["checks"]["source_mutation_not_allowed"] = (
        state_machine.get("source_mutation_allowed") is False
    )

    result["checks"]["broker_or_live_not_allowed"] = (
        state_machine.get("broker_or_live_allowed") is False
    )

    result["checks"]["recursive_execution_not_allowed"] = (
        state_machine.get("recursive_execution_allowed") is False
    )

    result["checks"]["autonomous_phase_execution_not_allowed"] = (
        state_machine.get("autonomous_phase_execution_allowed")
        is False
    )

    result["checks"]["has_next_read_only_phase"] = bool(
        state_machine.get(
            "recommended_next_read_only_phase"
        )
    )

    result["pipeline_summary"] = {
        "from":
            "55A_QWEN_READ_ONLY_ARCHITECTURE_STATE_MACHINE_STUB",

        "to":
            "55B_QWEN_READ_ONLY_ARCHITECTURE_STATE_MACHINE_ROLLUP_CERTIFICATION",

        "certified_capability": [
            "Qwen read-only architecture state machine contract exists",
            "state definitions are controlled",
            "allowed transitions are controlled",
            "forbidden transitions are controlled",
            "read-only behavior preserved",
            "no execution authority introduced",
            "no mutation authority introduced",
        ],

        "current_behavior": [
            "Qwen may evaluate declared read-only states",
            "Qwen may follow contract-defined summary paths",
            "Qwen may stop at terminal boundary",
            "Qwen may not execute state transitions autonomously",
            "Qwen may not mutate architecture state",
        ],

        "next_recommended_phase":
            "55C_HANDOFF_BUNDLE_REFRESH",
    }

    result["certified"] = all(
        result["checks"].values()
    )

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
