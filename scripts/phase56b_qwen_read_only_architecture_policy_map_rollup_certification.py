#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "56B_qwen_read_only_architecture_policy_map_rollup_certification_latest.json"
PHASE = "56B_QWEN_READ_ONLY_ARCHITECTURE_POLICY_MAP_ROLLUP_CERTIFICATION"

ARTIFACT = SANDBOX / "56A_qwen_read_only_architecture_policy_map_stub_latest.json"

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
    policy = data.get("policy_map_payload", {}) if isinstance(data.get("policy_map_payload"), dict) else {}
    domains = policy.get("policy_domains", {}) if isinstance(policy.get("policy_domains"), dict) else {}

    result["source_phase"] = data.get("phase")
    result["source_certified"] = data.get("certified") is True

    result["policy_summary"] = {
        "status": policy.get("status"),
        "policy_mode": policy.get("policy_mode"),
        "policy_domains": domains,
        "recommended_next_read_only_phase": policy.get("recommended_next_read_only_phase"),
    }

    result["checks"]["artifact_exists"] = ARTIFACT.exists()
    result["checks"]["source_certified"] = data.get("certified") is True
    result["checks"]["status_ok"] = policy.get("status") == "qwen_read_only_architecture_policy_map_ready"
    result["checks"]["mode_read_only"] = policy.get("policy_mode") == "read_only_policy_contract_only"
    result["checks"]["handoff_certified"] = policy.get("handoff_certified") is True
    result["checks"]["domains_present"] = len(domains) > 0
    result["checks"]["information_access_present"] = bool(domains.get("information_access"))
    result["checks"]["response_behavior_present"] = bool(domains.get("response_behavior"))
    result["checks"]["safety_boundaries_present"] = bool(domains.get("safety_boundaries"))
    result["checks"]["observations_allowed"] = policy.get("allowed_policy_observations") is True
    result["checks"]["policy_mutation_blocked"] = policy.get("policy_mutation_allowed") is False
    result["checks"]["runtime_policy_enforcement_blocked"] = policy.get("runtime_policy_enforcement_allowed") is False
    result["checks"]["execution_policy_blocked"] = policy.get("execution_policy_allowed") is False
    result["checks"]["source_policy_change_blocked"] = policy.get("source_policy_change_allowed") is False
    result["checks"]["actions_blocked"] = policy.get("actions_allowed") is False
    result["checks"]["writes_blocked"] = policy.get("writes_allowed") is False
    result["checks"]["runtime_blocked"] = policy.get("runtime_allowed") is False
    result["checks"]["source_mutation_blocked"] = policy.get("source_mutation_allowed") is False
    result["checks"]["broker_or_live_blocked"] = policy.get("broker_or_live_allowed") is False
    result["checks"]["has_next_read_only_phase"] = bool(policy.get("recommended_next_read_only_phase"))

    result["pipeline_summary"] = {
        "from": "56A_QWEN_READ_ONLY_ARCHITECTURE_POLICY_MAP_STUB",
        "to": "56B_QWEN_READ_ONLY_ARCHITECTURE_POLICY_MAP_ROLLUP_CERTIFICATION",
        "certified_capability": [
            "Qwen read-only architecture policy map exists",
            "policy domains are defined",
            "information access policy is observable only",
            "response behavior policy is observable only",
            "safety boundary policy is observable only",
            "policy mutation remains blocked",
            "runtime enforcement remains blocked",
            "execution and broker/live policy remain blocked",
        ],
        "current_behavior": [
            "Qwen may inspect policy map categories",
            "Qwen may summarize read-only policy boundaries",
            "Qwen may explain disabled policy capabilities",
            "Qwen may recommend read-only next phase only",
            "Qwen may not enforce or mutate policy",
        ],
        "next_recommended_phase": "56C_HANDOFF_BUNDLE_REFRESH",
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
