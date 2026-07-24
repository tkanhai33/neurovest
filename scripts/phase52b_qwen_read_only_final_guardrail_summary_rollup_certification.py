#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "52B_qwen_read_only_final_guardrail_summary_rollup_certification_latest.json"
PHASE = "52B_QWEN_READ_ONLY_FINAL_GUARDRAIL_SUMMARY_ROLLUP_CERTIFICATION"

ARTIFACT = SANDBOX / "52A_qwen_read_only_final_guardrail_summary_stub_latest.json"

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
    summary = data.get("guardrail_summary_payload", {}) if isinstance(data.get("guardrail_summary_payload"), dict) else {}

    result["source_phase"] = data.get("phase")
    result["source_certified"] = data.get("certified") is True
    result["guardrail_summary"] = {
        "status": summary.get("status"),
        "summary_mode": summary.get("summary_mode"),
        "allowed_capabilities": summary.get("allowed_capabilities", []),
        "guardrails_confirmed": summary.get("guardrails_confirmed", []),
        "recommended_next_read_only_phase": summary.get("recommended_next_read_only_phase"),
    }

    result["checks"]["artifact_exists"] = ARTIFACT.exists()
    result["checks"]["source_certified"] = data.get("certified") is True
    result["checks"]["status_ok"] = summary.get("status") == "qwen_read_only_final_guardrail_summary_ready"
    result["checks"]["summary_mode_read_only"] = summary.get("summary_mode") == "read_only_guardrail_summary_only"
    result["checks"]["handoff_certified"] = summary.get("handoff_certified") is True
    result["checks"]["allowed_capabilities_present"] = len(summary.get("allowed_capabilities", [])) > 0
    result["checks"]["guardrails_confirmed_present"] = len(summary.get("guardrails_confirmed", [])) > 0
    result["checks"]["summary_read_allowed"] = summary.get("summary_read_allowed") is True
    result["checks"]["actions_not_allowed"] = summary.get("actions_allowed") is False
    result["checks"]["writes_not_allowed"] = summary.get("writes_allowed") is False
    result["checks"]["runtime_not_allowed"] = summary.get("runtime_allowed") is False
    result["checks"]["shell_execution_not_allowed"] = summary.get("shell_execution_allowed") is False
    result["checks"]["source_mutation_not_allowed"] = summary.get("source_mutation_allowed") is False
    result["checks"]["broker_or_live_not_allowed"] = summary.get("broker_or_live_allowed") is False
    result["checks"]["recursive_execution_not_allowed"] = summary.get("recursive_execution_allowed") is False
    result["checks"]["autonomous_phase_execution_not_allowed"] = summary.get("autonomous_phase_execution_allowed") is False
    result["checks"]["has_next_read_only_phase"] = bool(summary.get("recommended_next_read_only_phase"))

    result["pipeline_summary"] = {
        "from": "52A_QWEN_READ_ONLY_FINAL_GUARDRAIL_SUMMARY_STUB",
        "to": "52B_QWEN_READ_ONLY_FINAL_GUARDRAIL_SUMMARY_ROLLUP_CERTIFICATION",
        "certified_capability": [
            "Qwen final read-only guardrail summary exists",
            "allowed capabilities are summarized",
            "guardrails are confirmed",
            "summary reading is allowed",
            "actions/writes/runtime/shell/source mutation remain blocked",
            "broker/live actions remain blocked",
            "recursive and autonomous phase execution remain blocked",
        ],
        "current_behavior": [
            "Qwen may summarize final read-only guardrails",
            "Qwen may list allowed read-only capabilities",
            "Qwen may list blocked capabilities",
            "Qwen may recommend read-only next phase only",
        ],
        "next_recommended_phase": "52C_HANDOFF_BUNDLE_REFRESH",
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
