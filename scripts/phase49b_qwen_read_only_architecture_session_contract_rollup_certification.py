#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "49B_qwen_read_only_architecture_session_contract_rollup_certification_latest.json"
PHASE = "49B_QWEN_READ_ONLY_ARCHITECTURE_SESSION_CONTRACT_ROLLUP_CERTIFICATION"

ARTIFACT = SANDBOX / "49A_qwen_read_only_architecture_session_contract_stub_latest.json"

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
    contract = data.get("session_contract", {}) if isinstance(data.get("session_contract"), dict) else {}
    session = contract.get("session_example", {}) if isinstance(contract.get("session_example"), dict) else {}

    result["source_phase"] = data.get("phase")
    result["source_certified"] = data.get("certified") is True
    result["session_summary"] = {
        "status": contract.get("status"),
        "contract_mode": contract.get("contract_mode"),
        "session_id": session.get("session_id"),
        "architecture_stage": session.get("architecture_stage"),
        "latest_confirmed_phase": session.get("latest_confirmed_phase"),
        "recommended_next_read_only_phase": contract.get("recommended_next_read_only_phase"),
    }

    result["checks"]["artifact_exists"] = ARTIFACT.exists()
    result["checks"]["source_certified"] = data.get("certified") is True
    result["checks"]["status_ok"] = contract.get("status") == "qwen_read_only_session_contract_ready"
    result["checks"]["contract_mode_read_only"] = contract.get("contract_mode") == "read_only_session_only"
    result["checks"]["required_fields_present"] = len(contract.get("required_session_fields", [])) > 0
    result["checks"]["forbidden_actions_present"] = len(contract.get("forbidden_session_actions", [])) > 0
    result["checks"]["session_example_present"] = bool(session)
    result["checks"]["session_read_allowed"] = contract.get("session_read_allowed") is True
    result["checks"]["session_write_blocked"] = contract.get("session_write_allowed") is False
    result["checks"]["actions_not_allowed"] = contract.get("actions_allowed") is False
    result["checks"]["writes_not_allowed"] = contract.get("writes_allowed") is False
    result["checks"]["runtime_not_allowed"] = contract.get("runtime_allowed") is False
    result["checks"]["source_mutation_not_allowed"] = contract.get("source_mutation_allowed") is False
    result["checks"]["broker_or_live_not_allowed"] = contract.get("broker_or_live_allowed") is False
    result["checks"]["critical_safety_locks_false"] = all(
        value is False
        for value in session.get("critical_safety_locks", {}).values()
    )
    result["checks"]["has_next_read_only_phase"] = bool(contract.get("recommended_next_read_only_phase"))

    result["pipeline_summary"] = {
        "from": "49A_QWEN_READ_ONLY_ARCHITECTURE_SESSION_CONTRACT_STUB",
        "to": "49B_QWEN_READ_ONLY_ARCHITECTURE_SESSION_CONTRACT_ROLLUP_CERTIFICATION",
        "certified_capability": [
            "Qwen read-only session contract exists",
            "session fields are defined",
            "forbidden session actions are defined",
            "session read is allowed",
            "session writes remain blocked",
            "actions/writes/runtime/source mutation remain blocked",
            "broker/live actions remain blocked",
        ],
        "current_behavior": [
            "Qwen may read session context only",
            "Qwen may summarize session architecture state",
            "Qwen may preserve locked safety boundary",
            "Qwen may not mutate or execute from session context",
        ],
        "next_recommended_phase": "49C_HANDOFF_BUNDLE_REFRESH",
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
