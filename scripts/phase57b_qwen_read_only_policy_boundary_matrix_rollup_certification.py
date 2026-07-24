#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "57B_qwen_read_only_policy_boundary_matrix_rollup_certification_latest.json"
PHASE = "57B_QWEN_READ_ONLY_POLICY_BOUNDARY_MATRIX_ROLLUP_CERTIFICATION"

ARTIFACT = SANDBOX / "57A_qwen_read_only_policy_boundary_matrix_stub_latest.json"

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
    matrix = (
        data.get("policy_boundary_matrix_payload", {})
        if isinstance(data.get("policy_boundary_matrix_payload"), dict)
        else {}
    )

    allowed = matrix.get("allowed_cells", {}) if isinstance(matrix.get("allowed_cells"), dict) else {}
    blocked = matrix.get("blocked_cells", {}) if isinstance(matrix.get("blocked_cells"), dict) else {}

    result["source_phase"] = data.get("phase")
    result["source_certified"] = data.get("certified") is True

    result["matrix_summary"] = {
        "status": matrix.get("status"),
        "matrix_mode": matrix.get("matrix_mode"),
        "allowed_cell_groups": sorted(allowed.keys()),
        "blocked_cell_groups": sorted(blocked.keys()),
        "recommended_next_read_only_phase": matrix.get("recommended_next_read_only_phase"),
    }

    result["checks"]["artifact_exists"] = ARTIFACT.exists()
    result["checks"]["source_certified"] = data.get("certified") is True
    result["checks"]["status_ok"] = matrix.get("status") == "qwen_read_only_policy_boundary_matrix_ready"
    result["checks"]["mode_read_only"] = matrix.get("matrix_mode") == "read_only_boundary_contract_only"
    result["checks"]["handoff_certified"] = matrix.get("handoff_certified") is True

    result["checks"]["allowed_cells_present"] = len(allowed) > 0
    result["checks"]["blocked_cells_present"] = len(blocked) > 0
    result["checks"]["information_access_allowed"] = bool(allowed.get("information_access"))
    result["checks"]["response_behavior_allowed"] = bool(allowed.get("response_behavior"))

    result["checks"]["mutation_blocked_group_present"] = bool(blocked.get("mutation"))
    result["checks"]["execution_blocked_group_present"] = bool(blocked.get("execution"))
    result["checks"]["trading_blocked_group_present"] = bool(blocked.get("trading"))
    result["checks"]["learning_promotion_blocked_group_present"] = bool(blocked.get("learning_promotion"))

    result["checks"]["matrix_read_allowed"] = matrix.get("matrix_read_allowed") is True
    result["checks"]["matrix_write_blocked"] = matrix.get("matrix_write_allowed") is False
    result["checks"]["matrix_enforcement_blocked"] = matrix.get("matrix_enforcement_allowed") is False

    result["checks"]["actions_blocked"] = matrix.get("actions_allowed") is False
    result["checks"]["writes_blocked"] = matrix.get("writes_allowed") is False
    result["checks"]["runtime_blocked"] = matrix.get("runtime_allowed") is False
    result["checks"]["shell_execution_blocked"] = matrix.get("shell_execution_allowed") is False
    result["checks"]["source_mutation_blocked"] = matrix.get("source_mutation_allowed") is False
    result["checks"]["policy_mutation_blocked"] = matrix.get("policy_mutation_allowed") is False
    result["checks"]["broker_or_live_blocked"] = matrix.get("broker_or_live_allowed") is False
    result["checks"]["recursive_execution_blocked"] = matrix.get("recursive_execution_allowed") is False
    result["checks"]["autonomous_phase_execution_blocked"] = matrix.get("autonomous_phase_execution_allowed") is False
    result["checks"]["has_next_read_only_phase"] = bool(matrix.get("recommended_next_read_only_phase"))

    result["pipeline_summary"] = {
        "from": "57A_QWEN_READ_ONLY_POLICY_BOUNDARY_MATRIX_STUB",
        "to": "57B_QWEN_READ_ONLY_POLICY_BOUNDARY_MATRIX_ROLLUP_CERTIFICATION",
        "certified_capability": [
            "Qwen read-only policy boundary matrix exists",
            "allowed cell groups are present",
            "blocked cell groups are present",
            "matrix read is allowed",
            "matrix write is blocked",
            "matrix enforcement is blocked",
            "mutation/execution/trading/learning-promotion boundaries remain blocked",
        ],
        "current_behavior": [
            "Qwen may inspect the policy boundary matrix",
            "Qwen may summarize allowed read-only cells",
            "Qwen may summarize blocked boundary cells",
            "Qwen may recommend read-only next phase only",
            "Qwen may not enforce, mutate, or execute from the matrix",
        ],
        "next_recommended_phase": "57C_HANDOFF_BUNDLE_REFRESH",
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
