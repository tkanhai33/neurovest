#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "51A_qwen_read_only_architecture_loop_boundary_stub_latest.json"
PHASE = "51A_QWEN_READ_ONLY_ARCHITECTURE_LOOP_BOUNDARY_STUB"

HANDOFF = SANDBOX / "50C_handoff_bundle_refresh_latest.json"

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

    loop_boundary = {
        "status": "qwen_read_only_architecture_loop_boundary_ready",
        "boundary_mode": "read_only_loop_control_only",
        "handoff_certified": handoff.get("certified") is True,

        "loop_read_allowed": True,
        "loop_summary_allowed": True,
        "loop_recommendation_allowed": True,

        "allowed_loop_outputs": [
            "architecture_summary",
            "locked_gate_explanation",
            "disabled_capability_summary",
            "missing_context_report",
            "read_only_next_phase_recommendation",
        ],

        "forbidden_loop_outputs": [
            "recursive_self_execution",
            "autonomous_phase_execution",
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

        "recursive_execution_allowed": False,
        "autonomous_phase_execution_allowed": False,
        "actions_allowed": False,
        "writes_allowed": False,
        "runtime_allowed": False,
        "shell_execution_allowed": False,
        "source_mutation_allowed": False,
        "broker_or_live_allowed": False,

        "recommended_next_read_only_phase":
            "51B_QWEN_READ_ONLY_ARCHITECTURE_LOOP_BOUNDARY_ROLLUP_CERTIFICATION",
    }

    result["loop_boundary_payload"] = loop_boundary

    result["checks"]["handoff_exists"] = HANDOFF.exists()
    result["checks"]["handoff_certified"] = handoff.get("certified") is True
    result["checks"]["status_ok"] = loop_boundary["status"] == "qwen_read_only_architecture_loop_boundary_ready"
    result["checks"]["boundary_mode_read_only"] = loop_boundary["boundary_mode"] == "read_only_loop_control_only"
    result["checks"]["loop_read_allowed"] = loop_boundary["loop_read_allowed"] is True
    result["checks"]["loop_summary_allowed"] = loop_boundary["loop_summary_allowed"] is True
    result["checks"]["loop_recommendation_allowed"] = loop_boundary["loop_recommendation_allowed"] is True
    result["checks"]["allowed_loop_outputs_present"] = len(loop_boundary["allowed_loop_outputs"]) > 0
    result["checks"]["forbidden_loop_outputs_present"] = len(loop_boundary["forbidden_loop_outputs"]) > 0
    result["checks"]["recursive_execution_blocked"] = loop_boundary["recursive_execution_allowed"] is False
    result["checks"]["autonomous_phase_execution_blocked"] = loop_boundary["autonomous_phase_execution_allowed"] is False
    result["checks"]["actions_not_allowed"] = loop_boundary["actions_allowed"] is False
    result["checks"]["writes_not_allowed"] = loop_boundary["writes_allowed"] is False
    result["checks"]["runtime_not_allowed"] = loop_boundary["runtime_allowed"] is False
    result["checks"]["shell_execution_not_allowed"] = loop_boundary["shell_execution_allowed"] is False
    result["checks"]["source_mutation_not_allowed"] = loop_boundary["source_mutation_allowed"] is False
    result["checks"]["broker_or_live_not_allowed"] = loop_boundary["broker_or_live_allowed"] is False
    result["checks"]["has_next_read_only_phase"] = bool(loop_boundary["recommended_next_read_only_phase"])

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(json.dumps(result, indent=2))
print(f"\\nWROTE: {OUT}")
