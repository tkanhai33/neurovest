#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "59B_qwen_read_only_final_handoff_certification_rollup_certification_latest.json"
PHASE = "59B_QWEN_READ_ONLY_FINAL_HANDOFF_CERTIFICATION_ROLLUP_CERTIFICATION"

ARTIFACT = SANDBOX / "59A_qwen_read_only_final_handoff_certification_stub_latest.json"

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

    payload = (
        data.get("final_handoff_payload", {})
        if isinstance(data.get("final_handoff_payload"), dict)
        else {}
    )

    snapshot = (
        payload.get("final_snapshot", {})
        if isinstance(payload.get("final_snapshot"), dict)
        else {}
    )

    result["source_phase"] = data.get("phase")
    result["source_certified"] = data.get("certified") is True

    result["final_handoff_summary"] = {
        "status": payload.get("status"),
        "handoff_mode": payload.get("handoff_mode"),
        "stage": snapshot.get("stage"),
        "latest_confirmed_phase": snapshot.get("latest_confirmed_phase"),
        "certified_read_only_capabilities": payload.get(
            "certified_read_only_capabilities",
            [],
        ),
        "permanently_blocked_capabilities": payload.get(
            "permanently_blocked_capabilities",
            [],
        ),
        "recommended_next_read_only_phase": payload.get(
            "recommended_next_read_only_phase"
        ),
    }

    result["checks"]["artifact_exists"] = ARTIFACT.exists()
    result["checks"]["source_certified"] = data.get("certified") is True
    result["checks"]["status_ok"] = (
        payload.get("status")
        == "qwen_read_only_final_handoff_certification_ready"
    )
    result["checks"]["mode_read_only"] = (
        payload.get("handoff_mode")
        == "read_only_final_handoff_only"
    )
    result["checks"]["handoff_certified"] = payload.get("handoff_certified") is True
    result["checks"]["snapshot_present"] = len(snapshot) > 0
    result["checks"]["capabilities_present"] = (
        len(payload.get("certified_read_only_capabilities", [])) > 0
    )
    result["checks"]["blocked_capabilities_present"] = (
        len(payload.get("permanently_blocked_capabilities", [])) > 0
    )

    result["checks"]["handoff_read_allowed"] = payload.get("handoff_read_allowed") is True
    result["checks"]["handoff_write_blocked"] = payload.get("handoff_write_allowed") is False
    result["checks"]["handoff_execution_blocked"] = payload.get("handoff_execution_allowed") is False
    result["checks"]["handoff_mutation_blocked"] = payload.get("handoff_mutation_allowed") is False

    result["checks"]["actions_blocked"] = payload.get("actions_allowed") is False
    result["checks"]["writes_blocked"] = payload.get("writes_allowed") is False
    result["checks"]["runtime_blocked"] = payload.get("runtime_allowed") is False
    result["checks"]["shell_execution_blocked"] = payload.get("shell_execution_allowed") is False
    result["checks"]["source_mutation_blocked"] = payload.get("source_mutation_allowed") is False
    result["checks"]["policy_mutation_blocked"] = payload.get("policy_mutation_allowed") is False
    result["checks"]["matrix_mutation_blocked"] = payload.get("matrix_mutation_allowed") is False
    result["checks"]["broker_or_live_blocked"] = payload.get("broker_or_live_allowed") is False
    result["checks"]["recursive_execution_blocked"] = payload.get("recursive_execution_allowed") is False
    result["checks"]["autonomous_phase_execution_blocked"] = payload.get("autonomous_phase_execution_allowed") is False

    result["checks"]["critical_safety_locks_false"] = all(
        value is False
        for value in snapshot.get("critical_safety_locks", {}).values()
    )

    result["checks"]["has_next_read_only_phase"] = bool(
        payload.get("recommended_next_read_only_phase")
    )

    result["pipeline_summary"] = {
        "from": "59A_QWEN_READ_ONLY_FINAL_HANDOFF_CERTIFICATION_STUB",
        "to": "59B_QWEN_READ_ONLY_FINAL_HANDOFF_CERTIFICATION_ROLLUP_CERTIFICATION",
        "certified_capability": [
            "Qwen final read-only handoff certification exists",
            "final handoff snapshot is present",
            "read-only capabilities are listed",
            "blocked capabilities are listed",
            "handoff read is allowed",
            "handoff write/execution/mutation are blocked",
            "runtime/shell/source/policy/matrix mutation remain blocked",
            "broker/live and recursive/autonomous execution remain blocked",
            "critical safety locks remain false",
        ],
        "current_behavior": [
            "Qwen may inspect final read-only handoff only",
            "Qwen may summarize certified read-only capability state",
            "Qwen may summarize permanently blocked capabilities",
            "Qwen may recommend read-only next phase only",
            "Qwen may not mutate, execute, enforce, or trade from handoff",
        ],
        "next_recommended_phase": "59C_HANDOFF_BUNDLE_REFRESH",
    }

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(json.dumps(result, indent=2))
print(f"\nWROTE: {OUT}")
