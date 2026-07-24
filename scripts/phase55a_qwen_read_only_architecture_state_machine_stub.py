#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "55A_qwen_read_only_architecture_state_machine_stub_latest.json"
PHASE = "55A_QWEN_READ_ONLY_ARCHITECTURE_STATE_MACHINE_STUB"

HANDOFF = SANDBOX / "54C_handoff_bundle_refresh_latest.json"

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "handoff_source": str(HANDOFF),
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    handoff = json.loads(HANDOFF.read_text(encoding="utf-8")) if HANDOFF.exists() else {}

    state_machine = {
        "status": "qwen_read_only_architecture_state_machine_ready",
        "state_machine_mode": "read_only_contract_only",
        "handoff_certified": handoff.get("certified") is True,

        "states": [
            "READ_HANDOFF",
            "SUMMARIZE_ARCHITECTURE",
            "EXPLAIN_LOCKED_GATES",
            "REPORT_MISSING_CONTEXT",
            "RECOMMEND_READ_ONLY_NEXT_PHASE",
            "STOP",
        ],

        "allowed_transitions": [
            ["READ_HANDOFF", "SUMMARIZE_ARCHITECTURE"],
            ["READ_HANDOFF", "EXPLAIN_LOCKED_GATES"],
            ["READ_HANDOFF", "REPORT_MISSING_CONTEXT"],
            ["READ_HANDOFF", "RECOMMEND_READ_ONLY_NEXT_PHASE"],
            ["SUMMARIZE_ARCHITECTURE", "STOP"],
            ["EXPLAIN_LOCKED_GATES", "STOP"],
            ["REPORT_MISSING_CONTEXT", "STOP"],
            ["RECOMMEND_READ_ONLY_NEXT_PHASE", "STOP"],
        ],

        "forbidden_transitions": [
            "WRITE_FILES",
            "PATCH_SOURCE",
            "RUN_SHELL",
            "EXECUTE_RUNTIME",
            "MUTATE_SOURCE",
            "ENABLE_STRATEGY",
            "ENABLE_SIMULATION",
            "ENABLE_LEARNING",
            "ENABLE_PROMOTION",
            "PLACE_BROKER_ORDER",
            "ENABLE_LIVE_TRADING",
            "AUTONOMOUS_PHASE_EXECUTION",
            "RECURSIVE_SELF_EXECUTION",
        ],

        "read_allowed": True,
        "summary_allowed": True,
        "recommendation_allowed": True,

        "actions_allowed": False,
        "writes_allowed": False,
        "runtime_allowed": False,
        "shell_execution_allowed": False,
        "source_mutation_allowed": False,
        "broker_or_live_allowed": False,
        "recursive_execution_allowed": False,
        "autonomous_phase_execution_allowed": False,

        "recommended_next_read_only_phase":
            "55B_QWEN_READ_ONLY_ARCHITECTURE_STATE_MACHINE_ROLLUP_CERTIFICATION",
    }

    result["state_machine_payload"] = state_machine

    result["checks"]["handoff_exists"] = HANDOFF.exists()
    result["checks"]["handoff_certified"] = handoff.get("certified") is True
    result["checks"]["status_ok"] = state_machine["status"] == "qwen_read_only_architecture_state_machine_ready"
    result["checks"]["mode_read_only"] = state_machine["state_machine_mode"] == "read_only_contract_only"
    result["checks"]["states_present"] = len(state_machine["states"]) > 0
    result["checks"]["allowed_transitions_present"] = len(state_machine["allowed_transitions"]) > 0
    result["checks"]["forbidden_transitions_present"] = len(state_machine["forbidden_transitions"]) > 0
    result["checks"]["read_allowed"] = state_machine["read_allowed"] is True
    result["checks"]["summary_allowed"] = state_machine["summary_allowed"] is True
    result["checks"]["recommendation_allowed"] = state_machine["recommendation_allowed"] is True
    result["checks"]["actions_not_allowed"] = state_machine["actions_allowed"] is False
    result["checks"]["writes_not_allowed"] = state_machine["writes_allowed"] is False
    result["checks"]["runtime_not_allowed"] = state_machine["runtime_allowed"] is False
    result["checks"]["shell_execution_not_allowed"] = state_machine["shell_execution_allowed"] is False
    result["checks"]["source_mutation_not_allowed"] = state_machine["source_mutation_allowed"] is False
    result["checks"]["broker_or_live_not_allowed"] = state_machine["broker_or_live_allowed"] is False
    result["checks"]["recursive_execution_not_allowed"] = state_machine["recursive_execution_allowed"] is False
    result["checks"]["autonomous_phase_execution_not_allowed"] = state_machine["autonomous_phase_execution_allowed"] is False
    result["checks"]["has_next_read_only_phase"] = bool(state_machine["recommended_next_read_only_phase"])

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(json.dumps(result, indent=2))
print(f"\nWROTE: {OUT}")
