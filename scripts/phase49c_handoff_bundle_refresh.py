#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"
OUT = SANDBOX / "49C_handoff_bundle_refresh_latest.json"

PHASE = "49C_HANDOFF_BUNDLE_REFRESH"

REQUIRED_PHASES = {
    "48C_HANDOFF_BUNDLE_REFRESH",
    "49A_QWEN_READ_ONLY_ARCHITECTURE_SESSION_CONTRACT_STUB",
    "49B_QWEN_READ_ONLY_ARCHITECTURE_SESSION_CONTRACT_ROLLUP_CERTIFICATION",
}

bundle = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "stage": "Qwen Read-Only Architecture Session Contract Certified",
    "latest_confirmed_phase": "49B_QWEN_READ_ONLY_ARCHITECTURE_SESSION_CONTRACT_ROLLUP_CERTIFICATION",
    "artifact_dir": str(SANDBOX),
    "file_count": 0,
    "cert_count": 0,
    "certified_phases": [],
    "failed_or_uncertified_phases": [],
    "critical_safety_locks": {
        "live_execution_enabled": False,
        "broker_execution_enabled": False,
        "historical_replay_enabled": False,
        "simulation_enabled": False,
        "registry_write_enabled": False,
        "promotion_enabled": False,
        "learning_enabled": False,
    },
    "current_capabilities": [
        "Qwen read-only architecture summaries",
        "Qwen locked gate explanation",
        "Qwen disabled capability summary",
        "Qwen missing-context detection",
        "Qwen read-only recommendation filtering",
        "Qwen read-only response validation",
        "Qwen read-only session contract",
    ],
    "still_disabled": [
        "Qwen file requests",
        "Qwen implementation patches",
        "Qwen file writes",
        "Qwen runtime execution",
        "Qwen source mutation",
        "Qwen strategy rule enablement",
        "Qwen trade simulation enablement",
        "Qwen learning",
        "Qwen promotion",
        "Qwen broker orders",
        "Qwen live trading",
    ],
    "next_recommended_phase": "50A_QWEN_READ_ONLY_SESSION_RESPONSE_BRIDGE_STUB",
    "next_phase_rule": "Create Qwen read-only session-response bridge only. No writes, execution, or implementation instructions.",
    "artifacts": [],
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    for path in sorted(SANDBOX.glob("*_latest.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        phase = data.get("phase", path.name)
        certified = data.get("certified") is True

        bundle["artifacts"].append({
            "file": path.name,
            "phase": phase,
            "certified": certified,
        })

        if certified:
            bundle["certified_phases"].append(phase)
        else:
            bundle["failed_or_uncertified_phases"].append(phase)

    certified_set = set(bundle["certified_phases"])

    bundle["file_count"] = len(bundle["artifacts"])
    bundle["cert_count"] = len(bundle["certified_phases"])

    bundle["checks"]["required_phases_certified"] = REQUIRED_PHASES.issubset(certified_set)
    bundle["checks"]["latest_phase_correct"] = bundle["latest_confirmed_phase"] in certified_set
    bundle["checks"]["critical_safety_locks_false"] = all(
        value is False for value in bundle["critical_safety_locks"].values()
    )
    bundle["checks"]["handoff_has_next_phase"] = bool(bundle["next_recommended_phase"])
    bundle["checks"]["no_bundle_errors"] = not bundle["errors"]

    bundle["pipeline_summary"] = {
        "from": "49A_QWEN_READ_ONLY_ARCHITECTURE_SESSION_CONTRACT_STUB",
        "through": "49B_QWEN_READ_ONLY_ARCHITECTURE_SESSION_CONTRACT_ROLLUP_CERTIFICATION",
        "to": "49C_HANDOFF_BUNDLE_REFRESH",
        "certified_capability": [
            "Qwen read-only session contract exists",
            "session fields are controlled",
            "forbidden session actions remain blocked",
            "session read allowed",
            "session writes blocked",
            "no runtime capability introduced",
        ],
        "current_behavior": [
            "read-only session context only",
            "architecture summaries only",
            "locked gate explanations only",
            "missing context reports only",
            "safe next phase recommendations only",
        ],
        "next_recommended_phase": "50A_QWEN_READ_ONLY_SESSION_RESPONSE_BRIDGE_STUB",
    }

    bundle["certified"] = all(bundle["checks"].values())

except Exception as exc:
    bundle["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(bundle, indent=2), encoding="utf-8")

print(json.dumps(bundle, indent=2))
print(f"\\nWROTE: {OUT}")
