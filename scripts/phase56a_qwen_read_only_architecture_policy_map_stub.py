#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "56A_qwen_read_only_architecture_policy_map_stub_latest.json"

PHASE = "56A_QWEN_READ_ONLY_ARCHITECTURE_POLICY_MAP_STUB"

HANDOFF = SANDBOX / "55C_handoff_bundle_refresh_latest.json"

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "handoff_source": str(HANDOFF),
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    handoff = (
        json.loads(HANDOFF.read_text(encoding="utf-8"))
        if HANDOFF.exists()
        else {}
    )

    policy_map = {
        "status":
            "qwen_read_only_architecture_policy_map_ready",

        "policy_mode":
            "read_only_policy_contract_only",

        "handoff_certified":
            handoff.get("certified") is True,

        "policy_domains": {
            "information_access": [
                "read_architecture_state",
                "read_certified_capabilities",
                "read_disabled_capabilities",
            ],

            "response_behavior": [
                "summarize",
                "explain",
                "report_missing_context",
                "recommend_read_only_next_phase",
            ],

            "safety_boundaries": [
                "no_mutation",
                "no_execution",
                "no_runtime_control",
                "no_broker_control",
            ],
        },

        "allowed_policy_observations": True,

        "policy_mutation_allowed": False,
        "runtime_policy_enforcement_allowed": False,
        "execution_policy_allowed": False,
        "source_policy_change_allowed": False,

        "actions_allowed": False,
        "writes_allowed": False,
        "runtime_allowed": False,
        "source_mutation_allowed": False,
        "broker_or_live_allowed": False,

        "recommended_next_read_only_phase":
            "56B_QWEN_READ_ONLY_ARCHITECTURE_POLICY_MAP_ROLLUP_CERTIFICATION",
    }

    result["policy_map_payload"] = policy_map

    result["checks"]["handoff_exists"] = HANDOFF.exists()
    result["checks"]["handoff_certified"] = (
        handoff.get("certified") is True
    )

    result["checks"]["status_ok"] = (
        policy_map["status"]
        ==
        "qwen_read_only_architecture_policy_map_ready"
    )

    result["checks"]["mode_read_only"] = (
        policy_map["policy_mode"]
        ==
        "read_only_policy_contract_only"
    )

    result["checks"]["domains_present"] = (
        len(policy_map["policy_domains"]) > 0
    )

    result["checks"]["observations_allowed"] = (
        policy_map["allowed_policy_observations"] is True
    )

    result["checks"]["mutation_blocked"] = (
        policy_map["policy_mutation_allowed"] is False
    )

    result["checks"]["runtime_blocked"] = (
        policy_map["runtime_policy_enforcement_allowed"] is False
    )

    result["checks"]["execution_blocked"] = (
        policy_map["execution_policy_allowed"] is False
    )

    result["checks"]["source_change_blocked"] = (
        policy_map["source_policy_change_allowed"] is False
    )

    result["checks"]["actions_blocked"] = (
        policy_map["actions_allowed"] is False
    )

    result["checks"]["writes_blocked"] = (
        policy_map["writes_allowed"] is False
    )

    result["checks"]["runtime_not_allowed"] = (
        policy_map["runtime_allowed"] is False
    )

    result["checks"]["source_mutation_not_allowed"] = (
        policy_map["source_mutation_allowed"] is False
    )

    result["checks"]["broker_or_live_not_allowed"] = (
        policy_map["broker_or_live_allowed"] is False
    )

    result["checks"]["next_phase_present"] = bool(
        policy_map["recommended_next_read_only_phase"]
    )

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
    encoding="utf-8",
)

print(json.dumps(result, indent=2))
print(f"\nWROTE: {OUT}")
