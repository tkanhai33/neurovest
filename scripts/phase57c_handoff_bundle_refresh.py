#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"
OUT = SANDBOX / "57C_handoff_bundle_refresh_latest.json"

PHASE = "57C_HANDOFF_BUNDLE_REFRESH"

SOURCES = [
    SANDBOX / "56C_handoff_bundle_refresh_latest.json",
    SANDBOX / "57B_qwen_read_only_policy_boundary_matrix_rollup_certification_latest.json",
]

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "sources": [str(x) for x in SOURCES],
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    loaded = {}

    for source in SOURCES:
        if source.exists():
            loaded[source.name] = json.loads(source.read_text(encoding="utf-8"))

    latest = loaded.get(
        "57B_qwen_read_only_policy_boundary_matrix_rollup_certification_latest.json",
        {},
    )

    result["handoff_snapshot"] = {
        "stage": "Qwen Read-Only Policy Boundary Matrix Certified",
        "latest_confirmed_phase": latest.get("phase"),

        "current_capabilities": [
            "Qwen read-only architecture summaries",
            "Qwen locked gate explanations",
            "Qwen disabled capability summaries",
            "Qwen response validation",
            "Qwen session contract",
            "Qwen session-response bridge",
            "Qwen loop boundary",
            "Qwen guardrail summary",
            "Qwen frozen handoff snapshot",
            "Qwen export summary",
            "Qwen architecture state machine contract",
            "Qwen architecture policy map contract",
            "Qwen policy boundary matrix contract",
        ],

        "still_disabled": [
            "file writes",
            "shell execution",
            "runtime execution",
            "source mutation",
            "policy mutation",
            "matrix mutation",
            "matrix enforcement",
            "runtime policy enforcement",
            "strategy enablement",
            "simulation enablement",
            "learning enablement",
            "promotion enablement",
            "broker execution",
            "live execution",
            "recursive execution",
            "autonomous phase execution",
        ],

        "critical_safety_locks": {
            "live_execution_enabled": False,
            "broker_execution_enabled": False,
            "simulation_enabled": False,
            "registry_write_enabled": False,
            "promotion_enabled": False,
            "learning_enabled": False,
        },

        "next_recommended_phase": "58A_QWEN_READ_ONLY_FINAL_CONTEXT_PACKAGE_STUB",
    }

    result["checks"]["source_present"] = len(loaded) == 2
    result["checks"]["policy_boundary_matrix_certified"] = latest.get("certified") is True
    result["checks"]["locks_false"] = all(
        value is False
        for value in result["handoff_snapshot"]["critical_safety_locks"].values()
    )
    result["checks"]["read_only_capabilities_present"] = (
        len(result["handoff_snapshot"]["current_capabilities"]) > 0
    )
    result["checks"]["disabled_capabilities_present"] = (
        len(result["handoff_snapshot"]["still_disabled"]) > 0
    )
    result["checks"]["next_phase_present"] = bool(
        result["handoff_snapshot"]["next_recommended_phase"]
    )

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(json.dumps(result, indent=2))
print(f"\nWROTE: {OUT}")
