#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "36C_enablement_gate_pipeline_rollup_certification_latest.json"
PHASE = "36C_ENABLEMENT_GATE_PIPELINE_ROLLUP_CERTIFICATION"

ARTIFACTS = [
    "36A_strategy_rule_enablement_gate_contract_stub_latest.json",
    "36B_enablement_gate_validation_stub_latest.json",
]

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "artifact_dir": str(SANDBOX),
    "artifact_results": [],
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    for name in ARTIFACTS:
        path = SANDBOX / name
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

        result["artifact_results"].append({
            "artifact": name,
            "exists": path.exists(),
            "phase": data.get("phase"),
            "certified": data.get("certified") is True,
            "checks": data.get("checks", {}),
        })

    all_checks = [
        item["checks"] for item in result["artifact_results"]
        if isinstance(item.get("checks"), dict)
    ]

    result["checks"]["all_artifacts_exist"] = all(x["exists"] for x in result["artifact_results"])
    result["checks"]["all_artifacts_certified"] = all(x["certified"] for x in result["artifact_results"])
    result["checks"]["rule_enablement_not_allowed_proven"] = any(c.get("rule_enablement_not_allowed") is True for c in all_checks)
    result["checks"]["entry_rules_disabled_proven"] = any(c.get("entry_rules_disabled") is True for c in all_checks)
    result["checks"]["exit_rules_disabled_proven"] = any(c.get("exit_rules_disabled") is True for c in all_checks)
    result["checks"]["trade_simulation_disabled_proven"] = any(c.get("trade_simulation_disabled") is True for c in all_checks)
    result["checks"]["unsafe_enabled_gate_rejected_proven"] = any(c.get("unsafe_enabled_gate_rejected") is True for c in all_checks)
    result["checks"]["broker_execution_disabled_proven"] = any(c.get("broker_execution_disabled") is True for c in all_checks)
    result["checks"]["live_execution_disabled_proven"] = any(c.get("live_execution_disabled") is True for c in all_checks)
    result["checks"]["all_safety_locks_false_proven"] = all(
        c.get("all_safety_locks_false") is True for c in all_checks if "all_safety_locks_false" in c
    )

    result["pipeline_summary"] = {
        "from": "36A_STRATEGY_RULE_ENABLEMENT_GATE_CONTRACT_STUB",
        "to": "36B_ENABLEMENT_GATE_VALIDATION_STUB",
        "certified_capability": [
            "strategy rule enablement gate contract",
            "locked gate validation",
            "unsafe enabled gate rejection",
        ],
        "current_behavior": [
            "rule enablement not allowed",
            "entry rules disabled",
            "exit rules disabled",
            "trade simulation disabled",
            "broker/live execution disabled",
        ],
        "next_recommended_phase": "36D_HANDOFF_BUNDLE_REFRESH",
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
