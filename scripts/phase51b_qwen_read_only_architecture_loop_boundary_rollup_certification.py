#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "51B_qwen_read_only_architecture_loop_boundary_rollup_certification_latest.json"
PHASE = "51B_QWEN_READ_ONLY_ARCHITECTURE_LOOP_BOUNDARY_ROLLUP_CERTIFICATION"

ARTIFACT = SANDBOX / "51A_qwen_read_only_architecture_loop_boundary_stub_latest.json"

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
    boundary = data.get("loop_boundary_payload", {}) if isinstance(data.get("loop_boundary_payload"), dict) else {}

    result["source_phase"] = data.get("phase")
    result["source_certified"] = data.get("certified") is True
    result["boundary_summary"] = {
        "status": boundary.get("status"),
        "boundary_mode": boundary.get("boundary_mode"),
        "allowed_loop_outputs": boundary.get("allowed_loop_outputs", []),
        "forbidden_loop_outputs": boundary.get("forbidden_loop_outputs", []),
        "recommended_next_read_only_phase": boundary.get("recommended_next_read_only_phase"),
    }

    result["checks"]["artifact_exists"] = ARTIFACT.exists()
    result["checks"]["source_certified"] = data.get("certified") is True
    result["checks"]["status_ok"] = boundary.get("status") == "qwen_read_only_architecture_loop_boundary_ready"
    result["checks"]["boundary_mode_read_only"] = boundary.get("boundary_mode") == "read_only_loop_control_only"
    result["checks"]["handoff_certified"] = boundary.get("handoff_certified") is True
    result["checks"]["loop_read_allowed"] = boundary.get("loop_read_allowed") is True
    result["checks"]["loop_summary_allowed"] = boundary.get("loop_summary_allowed") is True
    result["checks"]["loop_recommendation_allowed"] = boundary.get("loop_recommendation_allowed") is True
    result["checks"]["allowed_loop_outputs_present"] = len(boundary.get("allowed_loop_outputs", [])) > 0
    result["checks"]["forbidden_loop_outputs_present"] = len(boundary.get("forbidden_loop_outputs", [])) > 0
    result["checks"]["recursive_execution_blocked"] = boundary.get("recursive_execution_allowed") is False
    result["checks"]["autonomous_phase_execution_blocked"] = boundary.get("autonomous_phase_execution_allowed") is False
    result["checks"]["actions_not_allowed"] = boundary.get("actions_allowed") is False
    result["checks"]["writes_not_allowed"] = boundary.get("writes_allowed") is False
    result["checks"]["runtime_not_allowed"] = boundary.get("runtime_allowed") is False
    result["checks"]["shell_execution_not_allowed"] = boundary.get("shell_execution_allowed") is False
    result["checks"]["source_mutation_not_allowed"] = boundary.get("source_mutation_allowed") is False
    result["checks"]["broker_or_live_not_allowed"] = boundary.get("broker_or_live_allowed") is False
    result["checks"]["has_next_read_only_phase"] = bool(boundary.get("recommended_next_read_only_phase"))

    result["pipeline_summary"] = {
        "from": "51A_QWEN_READ_ONLY_ARCHITECTURE_LOOP_BOUNDARY_STUB",
        "to": "51B_QWEN_READ_ONLY_ARCHITECTURE_LOOP_BOUNDARY_ROLLUP_CERTIFICATION",
        "certified_capability": [
            "Qwen read-only architecture loop boundary exists",
            "loop read/summary/recommendation are allowed",
            "allowed loop outputs are controlled",
            "forbidden loop outputs remain blocked",
            "recursive self-execution is blocked",
            "autonomous phase execution is blocked",
            "actions/writes/runtime/shell/source mutation remain blocked",
            "broker/live actions remain blocked",
        ],
        "current_behavior": [
            "Qwen may stay inside read-only architecture loop only",
            "Qwen may summarize architecture state",
            "Qwen may explain locked gates",
            "Qwen may recommend read-only next phase only",
            "Qwen may not recursively execute or advance phases itself",
        ],
        "next_recommended_phase": "51C_HANDOFF_BUNDLE_REFRESH",
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
