#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"
OUT = SANDBOX / "47A_qwen_read_only_recommendation_filter_stub_latest.json"

PHASE = "47A_QWEN_READ_ONLY_RECOMMENDATION_FILTER_STUB"

HANDOFF = SANDBOX / "46C_handoff_bundle_refresh_latest.json"

ALLOWED_RECOMMENDATION_TYPES = {
    "read_only_next_phase",
    "missing_context_note",
    "locked_gate_explanation",
    "disabled_capability_summary",
}

FORBIDDEN_RECOMMENDATION_TYPES = {
    "implementation_patch",
    "file_write",
    "runtime_execution",
    "source_mutation",
    "strategy_rule_enablement",
    "trade_simulation_enablement",
    "learning_enablement",
    "promotion_enablement",
    "broker_execution",
    "live_execution",
}

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

    sample_recommendations = [
        {
            "type": "read_only_next_phase",
            "text": handoff.get("next_recommended_phase"),
            "allowed": True,
        },
        {
            "type": "locked_gate_explanation",
            "text": "Explain why strategy, risk, simulation, broker, and live gates remain locked.",
            "allowed": True,
        },
        {
            "type": "disabled_capability_summary",
            "text": "Summarize disabled capabilities without giving implementation instructions.",
            "allowed": True,
        },
    ]

    rejected_recommendations = [
        {
            "type": "implementation_patch",
            "text": "Write code to enable the next runtime step.",
            "allowed": False,
        },
        {
            "type": "runtime_execution",
            "text": "Run the sandbox runtime.",
            "allowed": False,
        },
        {
            "type": "broker_execution",
            "text": "Place a broker order.",
            "allowed": False,
        },
        {
            "type": "live_execution",
            "text": "Enable live trading.",
            "allowed": False,
        },
    ]

    filter_payload = {
        "status": "qwen_read_only_recommendation_filter_ready",
        "filter_mode": "read_only_recommendations_only",
        "allowed_recommendation_types": sorted(ALLOWED_RECOMMENDATION_TYPES),
        "forbidden_recommendation_types": sorted(FORBIDDEN_RECOMMENDATION_TYPES),
        "sample_recommendations": sample_recommendations,
        "rejected_recommendations": rejected_recommendations,
        "actions_allowed": False,
        "writes_allowed": False,
        "runtime_allowed": False,
        "source_mutation_allowed": False,
        "broker_or_live_allowed": False,
        "recommended_next_read_only_phase": "47B_QWEN_READ_ONLY_RECOMMENDATION_FILTER_ROLLUP_CERTIFICATION",
    }

    result["filter_payload"] = filter_payload

    result["checks"]["handoff_exists"] = HANDOFF.exists()
    result["checks"]["handoff_certified"] = handoff.get("certified") is True
    result["checks"]["status_ok"] = filter_payload["status"] == "qwen_read_only_recommendation_filter_ready"
    result["checks"]["filter_mode_read_only"] = filter_payload["filter_mode"] == "read_only_recommendations_only"
    result["checks"]["allowed_types_present"] = len(filter_payload["allowed_recommendation_types"]) > 0
    result["checks"]["forbidden_types_present"] = len(filter_payload["forbidden_recommendation_types"]) > 0
    result["checks"]["all_samples_allowed"] = all(x.get("allowed") is True for x in sample_recommendations)
    result["checks"]["all_rejected_blocked"] = all(x.get("allowed") is False for x in rejected_recommendations)
    result["checks"]["actions_not_allowed"] = filter_payload["actions_allowed"] is False
    result["checks"]["writes_not_allowed"] = filter_payload["writes_allowed"] is False
    result["checks"]["runtime_not_allowed"] = filter_payload["runtime_allowed"] is False
    result["checks"]["source_mutation_not_allowed"] = filter_payload["source_mutation_allowed"] is False
    result["checks"]["broker_or_live_not_allowed"] = filter_payload["broker_or_live_allowed"] is False
    result["checks"]["has_next_read_only_phase"] = bool(filter_payload["recommended_next_read_only_phase"])

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(json.dumps(result, indent=2))
print(f"\\nWROTE: {OUT}")
