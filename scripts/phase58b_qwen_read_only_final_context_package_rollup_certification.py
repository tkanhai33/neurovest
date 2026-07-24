#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "58B_qwen_read_only_final_context_package_rollup_certification_latest.json"
PHASE = "58B_QWEN_READ_ONLY_FINAL_CONTEXT_PACKAGE_ROLLUP_CERTIFICATION"

ARTIFACT = SANDBOX / "58A_qwen_read_only_final_context_package_stub_latest.json"

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
    package = (
        data.get("final_context_package_payload", {})
        if isinstance(data.get("final_context_package_payload"), dict)
        else {}
    )
    context = (
        package.get("context_package", {})
        if isinstance(package.get("context_package"), dict)
        else {}
    )

    result["source_phase"] = data.get("phase")
    result["source_certified"] = data.get("certified") is True

    result["context_package_summary"] = {
        "status": package.get("status"),
        "package_mode": package.get("package_mode"),
        "stage": context.get("stage"),
        "latest_confirmed_phase": context.get("latest_confirmed_phase"),
        "allowed_package_sections": package.get("allowed_package_sections", []),
        "forbidden_package_actions": package.get("forbidden_package_actions", []),
        "recommended_next_read_only_phase": package.get("recommended_next_read_only_phase"),
    }

    result["checks"]["artifact_exists"] = ARTIFACT.exists()
    result["checks"]["source_certified"] = data.get("certified") is True
    result["checks"]["status_ok"] = package.get("status") == "qwen_read_only_final_context_package_ready"
    result["checks"]["mode_read_only"] = package.get("package_mode") == "read_only_context_package_only"
    result["checks"]["handoff_certified"] = package.get("handoff_certified") is True
    result["checks"]["context_package_present"] = len(context) > 0
    result["checks"]["allowed_sections_present"] = len(package.get("allowed_package_sections", [])) > 0
    result["checks"]["forbidden_actions_present"] = len(package.get("forbidden_package_actions", [])) > 0

    result["checks"]["package_read_allowed"] = package.get("package_read_allowed") is True
    result["checks"]["package_write_blocked"] = package.get("package_write_allowed") is False
    result["checks"]["package_execution_blocked"] = package.get("package_execution_allowed") is False
    result["checks"]["package_mutation_blocked"] = package.get("package_mutation_allowed") is False

    result["checks"]["actions_blocked"] = package.get("actions_allowed") is False
    result["checks"]["writes_blocked"] = package.get("writes_allowed") is False
    result["checks"]["runtime_blocked"] = package.get("runtime_allowed") is False
    result["checks"]["shell_execution_blocked"] = package.get("shell_execution_allowed") is False
    result["checks"]["source_mutation_blocked"] = package.get("source_mutation_allowed") is False
    result["checks"]["policy_mutation_blocked"] = package.get("policy_mutation_allowed") is False
    result["checks"]["matrix_mutation_blocked"] = package.get("matrix_mutation_allowed") is False
    result["checks"]["broker_or_live_blocked"] = package.get("broker_or_live_allowed") is False
    result["checks"]["recursive_execution_blocked"] = package.get("recursive_execution_allowed") is False
    result["checks"]["autonomous_phase_execution_blocked"] = package.get("autonomous_phase_execution_allowed") is False

    result["checks"]["critical_safety_locks_false"] = all(
        value is False
        for value in context.get("critical_safety_locks", {}).values()
    )

    result["checks"]["has_next_read_only_phase"] = bool(
        package.get("recommended_next_read_only_phase")
    )

    result["pipeline_summary"] = {
        "from": "58A_QWEN_READ_ONLY_FINAL_CONTEXT_PACKAGE_STUB",
        "to": "58B_QWEN_READ_ONLY_FINAL_CONTEXT_PACKAGE_ROLLUP_CERTIFICATION",
        "certified_capability": [
            "Qwen final read-only context package exists",
            "context package sections are controlled",
            "forbidden package actions are controlled",
            "package read is allowed",
            "package write/execution/mutation are blocked",
            "runtime/shell/source/policy/matrix mutation remain blocked",
            "broker/live and recursive/autonomous execution remain blocked",
            "critical safety locks remain false",
        ],
        "current_behavior": [
            "Qwen may inspect final context package",
            "Qwen may summarize certified read-only architecture context",
            "Qwen may summarize disabled capabilities",
            "Qwen may recommend read-only next phase only",
            "Qwen may not mutate, execute, or enforce from package",
        ],
        "next_recommended_phase": "58C_HANDOFF_BUNDLE_REFRESH",
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
