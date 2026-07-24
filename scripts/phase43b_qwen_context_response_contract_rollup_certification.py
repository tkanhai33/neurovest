#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "43B_qwen_context_response_contract_rollup_certification_latest.json"
PHASE = "43B_QWEN_CONTEXT_RESPONSE_CONTRACT_ROLLUP_CERTIFICATION"

ARTIFACT = SANDBOX / "43A_qwen_context_response_contract_stub_latest.json"

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
    response = data.get("sample_response", {}) if isinstance(data.get("sample_response"), dict) else {}
    validation = data.get("validation", {}) if isinstance(data.get("validation"), dict) else {}

    result["source_phase"] = data.get("phase")
    result["source_certified"] = data.get("certified") is True
    result["response_summary"] = {
        "response_id": response.get("response_id"),
        "context_phase": response.get("context_phase"),
        "response_mode": response.get("response_mode"),
        "locked_gates": response.get("locked_gates", []),
        "recommended_next_read_only_phase": response.get("recommended_next_read_only_phase"),
        "actions_requested": response.get("actions_requested"),
        "writes_requested": response.get("writes_requested"),
        "runtime_requested": response.get("runtime_requested"),
        "broker_or_live_requested": response.get("broker_or_live_requested"),
    }

    result["checks"]["artifact_exists"] = ARTIFACT.exists()
    result["checks"]["source_certified"] = data.get("certified") is True
    result["checks"]["validation_certified"] = validation.get("certified") is True
    result["checks"]["response_mode_read_only"] = response.get("response_mode") == "read_only_summary_no_actions"
    result["checks"]["locked_gates_present"] = len(response.get("locked_gates", [])) > 0
    result["checks"]["has_next_read_only_phase"] = bool(response.get("recommended_next_read_only_phase"))
    result["checks"]["actions_not_requested"] = response.get("actions_requested") is False
    result["checks"]["writes_not_requested"] = response.get("writes_requested") is False
    result["checks"]["runtime_not_requested"] = response.get("runtime_requested") is False
    result["checks"]["broker_or_live_not_requested"] = response.get("broker_or_live_requested") is False

    result["pipeline_summary"] = {
        "from": "43A_QWEN_CONTEXT_RESPONSE_CONTRACT_STUB",
        "to": "43B_QWEN_CONTEXT_RESPONSE_CONTRACT_ROLLUP_CERTIFICATION",
        "certified_capability": [
            "Qwen response contract exists",
            "Qwen response is read-only",
            "Qwen response requests no actions",
            "Qwen response requests no writes",
            "Qwen response requests no runtime",
            "Qwen response requests no broker/live execution",
        ],
        "current_behavior": [
            "Qwen may produce summary-only architecture responses",
            "Qwen may list locked gates",
            "Qwen may recommend read-only next phase",
            "Qwen may not request or perform actions",
        ],
        "next_recommended_phase": "43C_HANDOFF_BUNDLE_REFRESH",
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
