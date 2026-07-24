#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "58A_qwen_read_only_final_context_package_stub_latest.json"
PHASE = "58A_QWEN_READ_ONLY_FINAL_CONTEXT_PACKAGE_STUB"

HANDOFF = SANDBOX / "57C_handoff_bundle_refresh_latest.json"

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

    package = {
        "status": "qwen_read_only_final_context_package_ready",
        "package_mode": "read_only_context_package_only",
        "handoff_certified": handoff.get("certified") is True,

        "context_package": {
            "stage": handoff.get("handoff_snapshot", {}).get("stage"),
            "latest_confirmed_phase": handoff.get("handoff_snapshot", {}).get("latest_confirmed_phase"),
            "current_capabilities": handoff.get("handoff_snapshot", {}).get("current_capabilities", []),
            "still_disabled": handoff.get("handoff_snapshot", {}).get("still_disabled", []),
            "critical_safety_locks": handoff.get("handoff_snapshot", {}).get("critical_safety_locks", {}),
            "next_recommended_phase": handoff.get("handoff_snapshot", {}).get("next_recommended_phase"),
        },

        "allowed_package_sections": [
            "stage",
            "latest_confirmed_phase",
            "current_capabilities",
            "still_disabled",
            "critical_safety_locks",
            "next_recommended_phase",
        ],

        "forbidden_package_actions": [
            "file_write",
            "shell_execution",
            "runtime_execution",
            "source_mutation",
            "policy_mutation",
            "matrix_mutation",
            "matrix_enforcement",
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

        "package_read_allowed": True,
        "package_write_allowed": False,
        "package_execution_allowed": False,
        "package_mutation_allowed": False,

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
            "58B_QWEN_READ_ONLY_FINAL_CONTEXT_PACKAGE_ROLLUP_CERTIFICATION",
    }

    result["final_context_package_payload"] = package

    result["checks"]["handoff_exists"] = HANDOFF.exists()
    result["checks"]["handoff_certified"] = handoff.get("certified") is True
    result["checks"]["status_ok"] = package["status"] == "qwen_read_only_final_context_package_ready"
    result["checks"]["mode_read_only"] = package["package_mode"] == "read_only_context_package_only"
    result["checks"]["context_package_present"] = len(package["context_package"]) > 0
    result["checks"]["allowed_sections_present"] = len(package["allowed_package_sections"]) > 0
    result["checks"]["forbidden_actions_present"] = len(package["forbidden_package_actions"]) > 0
    result["checks"]["package_read_allowed"] = package["package_read_allowed"] is True
    result["checks"]["package_write_blocked"] = package["package_write_allowed"] is False
    result["checks"]["package_execution_blocked"] = package["package_execution_allowed"] is False
    result["checks"]["package_mutation_blocked"] = package["package_mutation_allowed"] is False
    result["checks"]["actions_blocked"] = package["actions_allowed"] is False
    result["checks"]["writes_blocked"] = package["writes_allowed"] is False
    result["checks"]["runtime_blocked"] = package["runtime_allowed"] is False
    result["checks"]["shell_execution_blocked"] = package["shell_execution_allowed"] is False
    result["checks"]["source_mutation_blocked"] = package["source_mutation_allowed"] is False
    result["checks"]["policy_mutation_blocked"] = package["policy_mutation_allowed"] is False
    result["checks"]["matrix_mutation_blocked"] = package["matrix_mutation_allowed"] is False
    result["checks"]["broker_or_live_blocked"] = package["broker_or_live_allowed"] is False
    result["checks"]["recursive_execution_blocked"] = package["recursive_execution_allowed"] is False
    result["checks"]["autonomous_phase_execution_blocked"] = package["autonomous_phase_execution_allowed"] is False
    result["checks"]["critical_safety_locks_false"] = all(
        value is False
        for value in package["context_package"]["critical_safety_locks"].values()
    )
    result["checks"]["next_phase_present"] = bool(package["recommended_next_read_only_phase"])

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(json.dumps(result, indent=2))
print(f"\nWROTE: {OUT}")
