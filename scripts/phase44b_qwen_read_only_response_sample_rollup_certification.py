#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "44B_qwen_read_only_response_sample_rollup_certification_latest.json"
PHASE = "44B_QWEN_READ_ONLY_RESPONSE_SAMPLE_ROLLUP_CERTIFICATION"

ARTIFACT = SANDBOX / "44A_qwen_read_only_response_sample_stub_latest.json"

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
    sample = data.get("sample_response", {}) if isinstance(data.get("sample_response"), dict) else {}

    result["source_phase"] = data.get("phase")
    result["source_certified"] = data.get("certified") is True
    result["sample_summary"] = {
        "response_id": sample.get("response_id"),
        "response_mode": sample.get("response_mode"),
        "locked_gates": sample.get("locked_gates", []),
        "allowed_outputs_used": sample.get("allowed_outputs_used", []),
        "forbidden_outputs_requested": sample.get("forbidden_outputs_requested", []),
        "recommended_next_read_only_phase": sample.get("recommended_next_read_only_phase"),
    }

    result["checks"]["artifact_exists"] = ARTIFACT.exists()
    result["checks"]["source_certified"] = data.get("certified") is True
    result["checks"]["response_mode_read_only"] = sample.get("response_mode") == "read_only_summary_no_actions"
    result["checks"]["locked_gates_present"] = len(sample.get("locked_gates", [])) > 0
    result["checks"]["allowed_outputs_used_present"] = len(sample.get("allowed_outputs_used", [])) > 0
    result["checks"]["forbidden_outputs_empty"] = sample.get("forbidden_outputs_requested") == []
    result["checks"]["actions_not_requested"] = sample.get("actions_requested") is False
    result["checks"]["writes_not_requested"] = sample.get("writes_requested") is False
    result["checks"]["runtime_not_requested"] = sample.get("runtime_requested") is False
    result["checks"]["source_mutation_not_requested"] = sample.get("source_mutation_requested") is False
    result["checks"]["broker_or_live_not_requested"] = sample.get("broker_or_live_requested") is False
    result["checks"]["has_next_read_only_phase"] = bool(sample.get("recommended_next_read_only_phase"))

    result["pipeline_summary"] = {
        "from": "44A_QWEN_READ_ONLY_RESPONSE_SAMPLE_STUB",
        "to": "44B_QWEN_READ_ONLY_RESPONSE_SAMPLE_ROLLUP_CERTIFICATION",
        "certified_capability": [
            "sample Qwen read-only response exists",
            "sample response is read-only",
            "sample response lists locked gates",
            "sample response requests no actions",
            "sample response requests no writes/runtime/source mutation",
            "sample response requests no broker/live execution",
        ],
        "current_behavior": [
            "Qwen sample response is architecture summary only",
            "no action request",
            "no write request",
            "no runtime request",
            "no broker/live request",
        ],
        "next_recommended_phase": "44C_HANDOFF_BUNDLE_REFRESH",
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
