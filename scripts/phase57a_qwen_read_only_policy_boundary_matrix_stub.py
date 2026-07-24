#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "57A_qwen_read_only_policy_boundary_matrix_stub_latest.json"
PHASE = "57A_QWEN_READ_ONLY_POLICY_BOUNDARY_MATRIX_STUB"

HANDOFF = SANDBOX / "56C_handoff_bundle_refresh_latest.json"

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

    matrix = {
        "status": "qwen_read_only_policy_boundary_matrix_ready",
        "matrix_mode": "read_only_boundary_contract_only",
        "handoff_certified": handoff.get("certified") is True,

        "allowed_cells": {
            "information_access": [
                "read_architecture_state",
                "read_certified_capabilities",
                "read_disabled_capabilities",
            ],
            "response_behavior": [
                "summarize",
                "explain_locked_gates",
                "report_missing_context",
                "recommend_read_only_next_phase",
            ],
        },

        "blocked_cells": {
            "mutation": [
                "file_write",
                "source_mutation",
                "policy_mutation",
                "snapshot_mutation",
                "export_mutation",
            ],
            "execution": [
                "shell_execution",
                "runtime_execution",
                "recursive_self_execution",
                "autonomous_phase_execution",
            ],
            "trading": [
                "strategy_enablement",
                "simulation_enablement",
                "broker_execution",
                "live_execution",
            ],
            "learning_promotion": [
                "learning_enablement",
                "promotion_enablement",
            ],
        },

        "matrix_read_allowed": True,
        "matrix_write_allowed": False,
        "matrix_enforcement_allowed": False,

        "actions_allowed": False,
        "writes_allowed": False,
        "runtime_allowed": False,
        "shell_execution_allowed": False,
        "source_mutation_allowed": False,
        "policy_mutation_allowed": False,
        "broker_or_live_allowed": False,
        "recursive_execution_allowed": False,
        "autonomous_phase_execution_allowed": False,

        "recommended_next_read_only_phase":
            "57B_QWEN_READ_ONLY_POLICY_BOUNDARY_MATRIX_ROLLUP_CERTIFICATION",
    }

    result["policy_boundary_matrix_payload"] = matrix

    result["checks"]["handoff_exists"] = HANDOFF.exists()
    result["checks"]["handoff_certified"] = handoff.get("certified") is True
    result["checks"]["status_ok"] = matrix["status"] == "qwen_read_only_policy_boundary_matrix_ready"
    result["checks"]["mode_read_only"] = matrix["matrix_mode"] == "read_only_boundary_contract_only"
    result["checks"]["allowed_cells_present"] = len(matrix["allowed_cells"]) > 0
    result["checks"]["blocked_cells_present"] = len(matrix["blocked_cells"]) > 0
    result["checks"]["matrix_read_allowed"] = matrix["matrix_read_allowed"] is True
    result["checks"]["matrix_write_blocked"] = matrix["matrix_write_allowed"] is False
    result["checks"]["matrix_enforcement_blocked"] = matrix["matrix_enforcement_allowed"] is False
    result["checks"]["actions_blocked"] = matrix["actions_allowed"] is False
    result["checks"]["writes_blocked"] = matrix["writes_allowed"] is False
    result["checks"]["runtime_blocked"] = matrix["runtime_allowed"] is False
    result["checks"]["shell_execution_blocked"] = matrix["shell_execution_allowed"] is False
    result["checks"]["source_mutation_blocked"] = matrix["source_mutation_allowed"] is False
    result["checks"]["policy_mutation_blocked"] = matrix["policy_mutation_allowed"] is False
    result["checks"]["broker_or_live_blocked"] = matrix["broker_or_live_allowed"] is False
    result["checks"]["recursive_execution_blocked"] = matrix["recursive_execution_allowed"] is False
    result["checks"]["autonomous_phase_execution_blocked"] = matrix["autonomous_phase_execution_allowed"] is False
    result["checks"]["next_phase_present"] = bool(matrix["recommended_next_read_only_phase"])

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(json.dumps(result, indent=2))
print(f"\nWROTE: {OUT}")
