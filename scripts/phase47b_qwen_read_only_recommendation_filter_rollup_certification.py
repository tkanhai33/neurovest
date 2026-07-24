#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "47B_qwen_read_only_recommendation_filter_rollup_certification_latest.json"
PHASE = "47B_QWEN_READ_ONLY_RECOMMENDATION_FILTER_ROLLUP_CERTIFICATION"

ARTIFACT = SANDBOX / "47A_qwen_read_only_recommendation_filter_stub_latest.json"

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
    payload = data.get("filter_payload", {}) if isinstance(data.get("filter_payload"), dict) else {}

    result["source_phase"] = data.get("phase")
    result["source_certified"] = data.get("certified") is True
    result["filter_summary"] = {
        "status": payload.get("status"),
        "filter_mode": payload.get("filter_mode"),
        "allowed_recommendation_types": payload.get("allowed_recommendation_types", []),
        "forbidden_recommendation_types": payload.get("forbidden_recommendation_types", []),
        "recommended_next_read_only_phase": payload.get("recommended_next_read_only_phase"),
    }

    result["checks"]["artifact_exists"] = ARTIFACT.exists()
    result["checks"]["source_certified"] = data.get("certified") is True
    result["checks"]["status_ok"] = payload.get("status") == "qwen_read_only_recommendation_filter_ready"
    result["checks"]["filter_mode_read_only"] = payload.get("filter_mode") == "read_only_recommendations_only"
    result["checks"]["allowed_types_present"] = len(payload.get("allowed_recommendation_types", [])) > 0
    result["checks"]["forbidden_types_present"] = len(payload.get("forbidden_recommendation_types", [])) > 0
    result["checks"]["sample_recommendations_allowed"] = all(
        x.get("allowed") is True for x in payload.get("sample_recommendations", [])
    )
    result["checks"]["rejected_recommendations_blocked"] = all(
        x.get("allowed") is False for x in payload.get("rejected_recommendations", [])
    )
    result["checks"]["actions_not_allowed"] = payload.get("actions_allowed") is False
    result["checks"]["writes_not_allowed"] = payload.get("writes_allowed") is False
    result["checks"]["runtime_not_allowed"] = payload.get("runtime_allowed") is False
    result["checks"]["source_mutation_not_allowed"] = payload.get("source_mutation_allowed") is False
    result["checks"]["broker_or_live_not_allowed"] = payload.get("broker_or_live_allowed") is False
    result["checks"]["has_next_read_only_phase"] = bool(payload.get("recommended_next_read_only_phase"))

    result["pipeline_summary"] = {
        "from": "47A_QWEN_READ_ONLY_RECOMMENDATION_FILTER_STUB",
        "to": "47B_QWEN_READ_ONLY_RECOMMENDATION_FILTER_ROLLUP_CERTIFICATION",
        "certified_capability": [
            "Qwen read-only recommendation filter exists",
            "allowed recommendation types are defined",
            "forbidden recommendation types are defined",
            "safe recommendations pass",
            "unsafe recommendations are blocked",
            "actions/writes/runtime/source mutation remain blocked",
            "broker/live recommendations remain blocked",
        ],
        "current_behavior": [
            "Qwen may recommend read-only next phase only",
            "Qwen may explain locked gates",
            "Qwen may summarize disabled capabilities",
            "Qwen may not recommend implementation or execution",
        ],
        "next_recommended_phase": "47C_HANDOFF_BUNDLE_REFRESH",
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
