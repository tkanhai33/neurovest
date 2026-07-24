#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "50B_qwen_read_only_session_response_bridge_rollup_certification_latest.json"
PHASE = "50B_QWEN_READ_ONLY_SESSION_RESPONSE_BRIDGE_ROLLUP_CERTIFICATION"

ARTIFACT = SANDBOX / "50A_qwen_read_only_session_response_bridge_stub_latest.json"

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "artifact": str(ARTIFACT),
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    data = json.loads(ARTIFACT.read_text(encoding="utf-8")) if ARTIFACT.exists() else {}
    bridge = data.get("bridge_payload", {}) if isinstance(data.get("bridge_payload"), dict) else {}

    result["source_phase"] = data.get("phase")
    result["source_certified"] = data.get("certified") is True
    result["bridge_summary"] = {
        "status": bridge.get("status"),
        "bridge_mode": bridge.get("bridge_mode"),
        "allowed_response_uses": bridge.get("allowed_response_uses", []),
        "forbidden_bridge_actions": bridge.get("forbidden_bridge_actions", []),
        "recommended_next_read_only_phase": bridge.get("recommended_next_read_only_phase"),
    }

    result["checks"]["artifact_exists"] = ARTIFACT.exists()
    result["checks"]["source_certified"] = data.get("certified") is True
    result["checks"]["status_ok"] = bridge.get("status") == "qwen_read_only_session_response_bridge_ready"
    result["checks"]["bridge_mode_read_only"] = bridge.get("bridge_mode") == "read_only_session_to_response_only"
    result["checks"]["handoff_certified"] = bridge.get("handoff_certified") is True
    result["checks"]["session_context_read_allowed"] = bridge.get("session_context_read_allowed") is True
    result["checks"]["response_generation_allowed"] = bridge.get("response_generation_allowed") is True
    result["checks"]["allowed_response_uses_present"] = len(bridge.get("allowed_response_uses", [])) > 0
    result["checks"]["forbidden_bridge_actions_present"] = len(bridge.get("forbidden_bridge_actions", [])) > 0
    result["checks"]["actions_not_allowed"] = bridge.get("actions_allowed") is False
    result["checks"]["writes_not_allowed"] = bridge.get("writes_allowed") is False
    result["checks"]["runtime_not_allowed"] = bridge.get("runtime_allowed") is False
    result["checks"]["shell_execution_not_allowed"] = bridge.get("shell_execution_allowed") is False
    result["checks"]["source_mutation_not_allowed"] = bridge.get("source_mutation_allowed") is False
    result["checks"]["broker_or_live_not_allowed"] = bridge.get("broker_or_live_allowed") is False
    result["checks"]["has_next_read_only_phase"] = bool(bridge.get("recommended_next_read_only_phase"))

    result["pipeline_summary"] = {
        "from": "50A_QWEN_READ_ONLY_SESSION_RESPONSE_BRIDGE_STUB",
        "to": "50B_QWEN_READ_ONLY_SESSION_RESPONSE_BRIDGE_ROLLUP_CERTIFICATION",
        "certified_capability": [
            "Qwen read-only session-response bridge exists",
            "session context read is allowed",
            "read-only response generation is allowed",
            "allowed response uses are controlled",
            "forbidden bridge actions remain blocked",
            "actions/writes/runtime/shell/source mutation remain blocked",
            "broker/live actions remain blocked",
        ],
        "current_behavior": [
            "Qwen may bridge session context into read-only responses only",
            "Qwen may summarize architecture from session context",
            "Qwen may explain locked gates from session context",
            "Qwen may recommend read-only next phase only",
            "Qwen may not mutate or execute through the bridge",
        ],
        "next_recommended_phase": "50C_HANDOFF_BUNDLE_REFRESH",
    }

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(json.dumps(result, indent=2))
print(f"\\nWROTE: {OUT}")
