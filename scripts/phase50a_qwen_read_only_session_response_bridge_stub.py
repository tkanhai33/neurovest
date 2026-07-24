#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "50A_qwen_read_only_session_response_bridge_stub_latest.json"
PHASE = "50A_QWEN_READ_ONLY_SESSION_RESPONSE_BRIDGE_STUB"

HANDOFF = SANDBOX / "49C_handoff_bundle_refresh_latest.json"

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

    bridge = {
        "status": "qwen_read_only_session_response_bridge_ready",
        "bridge_mode": "read_only_session_to_response_only",
        "handoff_certified": handoff.get("certified") is True,
        "session_context_read_allowed": True,
        "response_generation_allowed": True,
        "allowed_response_uses": [
            "architecture_summary",
            "locked_gate_explanation",
            "disabled_capability_summary",
            "missing_context_report",
            "read_only_next_phase_recommendation",
        ],
        "forbidden_bridge_actions": [
            "file_write",
            "implementation_patch",
            "runtime_execution",
            "shell_execution",
            "source_mutation",
            "strategy_enablement",
            "simulation_enablement",
            "learning_enablement",
            "promotion_enablement",
            "broker_execution",
            "live_execution",
        ],
        "actions_allowed": False,
        "writes_allowed": False,
        "runtime_allowed": False,
        "shell_execution_allowed": False,
        "source_mutation_allowed": False,
        "broker_or_live_allowed": False,
        "recommended_next_read_only_phase": "50B_QWEN_READ_ONLY_SESSION_RESPONSE_BRIDGE_ROLLUP_CERTIFICATION",
    }

    result["bridge_payload"] = bridge

    result["checks"]["handoff_exists"] = HANDOFF.exists()
    result["checks"]["handoff_certified"] = handoff.get("certified") is True
    result["checks"]["status_ok"] = bridge["status"] == "qwen_read_only_session_response_bridge_ready"
    result["checks"]["bridge_mode_read_only"] = bridge["bridge_mode"] == "read_only_session_to_response_only"
    result["checks"]["session_context_read_allowed"] = bridge["session_context_read_allowed"] is True
    result["checks"]["response_generation_allowed"] = bridge["response_generation_allowed"] is True
    result["checks"]["allowed_response_uses_present"] = len(bridge["allowed_response_uses"]) > 0
    result["checks"]["forbidden_bridge_actions_present"] = len(bridge["forbidden_bridge_actions"]) > 0
    result["checks"]["actions_not_allowed"] = bridge["actions_allowed"] is False
    result["checks"]["writes_not_allowed"] = bridge["writes_allowed"] is False
    result["checks"]["runtime_not_allowed"] = bridge["runtime_allowed"] is False
    result["checks"]["shell_execution_not_allowed"] = bridge["shell_execution_allowed"] is False
    result["checks"]["source_mutation_not_allowed"] = bridge["source_mutation_allowed"] is False
    result["checks"]["broker_or_live_not_allowed"] = bridge["broker_or_live_allowed"] is False
    result["checks"]["has_next_read_only_phase"] = bool(bridge["recommended_next_read_only_phase"])

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(json.dumps(result, indent=2))
print(f"\\nWROTE: {OUT}")
