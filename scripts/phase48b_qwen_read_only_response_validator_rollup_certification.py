#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "48B_qwen_read_only_response_validator_rollup_certification_latest.json"

PHASE = "48B_QWEN_READ_ONLY_RESPONSE_VALIDATOR_ROLLUP_CERTIFICATION"

ARTIFACT = SANDBOX / "48A_qwen_read_only_response_validator_stub_latest.json"

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "artifact": str(ARTIFACT),
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    data = (
        json.loads(ARTIFACT.read_text(encoding="utf-8"))
        if ARTIFACT.exists()
        else {}
    )

    payload = (
        data.get("validator_payload", {})
        if isinstance(data.get("validator_payload"), dict)
        else {}
    )

    result["source_phase"] = data.get("phase")
    result["source_certified"] = data.get("certified") is True

    result["validator_summary"] = {
        "status": payload.get("status"),
        "validator_mode": payload.get("validator_mode"),
        "allowed_response_types": payload.get(
            "allowed_response_types",
            []
        ),
        "forbidden_response_types": payload.get(
            "forbidden_response_types",
            []
        ),
        "recommended_next_read_only_phase": payload.get(
            "recommended_next_read_only_phase"
        ),
    }

    result["checks"]["artifact_exists"] = ARTIFACT.exists()

    result["checks"]["source_certified"] = (
        data.get("certified") is True
    )

    result["checks"]["status_ok"] = (
        payload.get("status")
        == "qwen_read_only_response_validator_ready"
    )

    result["checks"]["validator_mode_read_only"] = (
        payload.get("validator_mode")
        == "read_only_response_validation_only"
    )

    result["checks"]["allowed_response_types_present"] = (
        len(payload.get("allowed_response_types", [])) > 0
    )

    result["checks"]["forbidden_response_types_present"] = (
        len(payload.get("forbidden_response_types", [])) > 0
    )

    result["checks"]["allowed_samples_valid"] = all(
        item.get("allowed") is True
        for item in payload.get(
            "sample_allowed_responses",
            []
        )
    )

    result["checks"]["blocked_samples_valid"] = all(
        item.get("allowed") is False
        for item in payload.get(
            "sample_blocked_responses",
            []
        )
    )

    result["checks"]["response_validation_allowed"] = (
        payload.get("response_validation_allowed")
        is True
    )

    result["checks"]["actions_not_allowed"] = (
        payload.get("actions_allowed")
        is False
    )

    result["checks"]["writes_not_allowed"] = (
        payload.get("writes_allowed")
        is False
    )

    result["checks"]["runtime_not_allowed"] = (
        payload.get("runtime_allowed")
        is False
    )

    result["checks"]["source_mutation_not_allowed"] = (
        payload.get("source_mutation_allowed")
        is False
    )

    result["checks"]["broker_or_live_not_allowed"] = (
        payload.get("broker_or_live_allowed")
        is False
    )

    result["checks"]["has_next_read_only_phase"] = bool(
        payload.get(
            "recommended_next_read_only_phase"
        )
    )

    result["pipeline_summary"] = {
        "from":
            "48A_QWEN_READ_ONLY_RESPONSE_VALIDATOR_STUB",

        "to":
            "48B_QWEN_READ_ONLY_RESPONSE_VALIDATOR_ROLLUP_CERTIFICATION",

        "certified_capability": [
            "Qwen response validator exists",
            "response classes are controlled",
            "allowed responses pass",
            "blocked responses remain rejected",
            "read-only boundary preserved",
            "no runtime capability introduced",
        ],

        "current_behavior": [
            "architecture summaries only",
            "locked gate explanations only",
            "missing context reports only",
            "safe next phase recommendations only",
        ],

        "next_recommended_phase":
            "48C_HANDOFF_BUNDLE_REFRESH",
    }

    result["certified"] = all(
        result["checks"].values()
    )

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })


OUT.write_text(
    json.dumps(result, indent=2),
    encoding="utf-8"
)

print(json.dumps(result, indent=2))
print(f"\nWROTE: {OUT}")
