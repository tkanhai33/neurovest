#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "38C_risk_gate_pipeline_rollup_certification_latest.json"
PHASE = "38C_RISK_GATE_PIPELINE_ROLLUP_CERTIFICATION"

ARTIFACTS = [
    "38A_risk_gate_contract_stub_latest.json",
    "38B_risk_gate_validation_stub_latest.json",
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
    result["checks"]["risk_gate_not_passed_proven"] = any(c.get("risk_gate_not_passed") is True for c in all_checks)
    result["checks"]["risk_approval_absent_proven"] = any(c.get("risk_approval_absent") is True for c in all_checks)
    result["checks"]["unsafe_gate_rejected_proven"] = any(c.get("unsafe_gate_rejected") is True for c in all_checks)
    result["checks"]["trade_simulation_not_allowed_proven"] = any(c.get("trade_simulation_not_allowed") is True for c in all_checks)
    result["checks"]["trade_simulation_disabled_proven"] = any(c.get("trade_simulation_disabled") is True for c in all_checks)
    result["checks"]["broker_execution_disabled_proven"] = any(c.get("broker_execution_disabled") is True for c in all_checks)
    result["checks"]["live_execution_disabled_proven"] = any(c.get("live_execution_disabled") is True for c in all_checks)
    result["checks"]["all_safety_locks_false_proven"] = all(
        c.get("all_safety_locks_false") is True
        for c in all_checks
        if "all_safety_locks_false" in c
    )

    result["pipeline_summary"] = {
        "from": "38A_RISK_GATE_CONTRACT_STUB",
        "to": "38B_RISK_GATE_VALIDATION_STUB",
        "certified_capability": [
            "risk gate contract",
            "locked risk gate validation",
            "unsafe passed risk gate rejection",
        ],
        "current_behavior": [
            "risk gate not passed",
            "risk approval absent",
            "trade simulation not allowed",
            "trade simulation disabled",
            "broker/live execution disabled",
        ],
        "next_recommended_phase": "38D_HANDOFF_BUNDLE_REFRESH",
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
