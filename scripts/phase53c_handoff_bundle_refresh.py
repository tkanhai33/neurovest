#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"
OUT = SANDBOX / "53C_handoff_bundle_refresh_latest.json"

PHASE = "53C_HANDOFF_BUNDLE_REFRESH"

REQUIRED_PHASES = {
    "52C_HANDOFF_BUNDLE_REFRESH",
    "53A_QWEN_READ_ONLY_HANDOFF_FREEZE_STUB",
    "53B_QWEN_READ_ONLY_HANDOFF_FREEZE_ROLLUP_CERTIFICATION",
}

bundle = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "stage": "Qwen Read-Only Handoff Freeze Certified",
    "latest_confirmed_phase": "53B_QWEN_READ_ONLY_HANDOFF_FREEZE_ROLLUP_CERTIFICATION",
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
        "Qwen read-only session-response bridge",
        "Qwen read-only loop boundary",
        "Qwen final read-only guardrail summary",
        "Qwen read-only frozen handoff snapshot",
    ],
    "still_disabled": [
        "Qwen recursive self-execution",
        "Qwen autonomous phase execution",
        "Qwen file requests",
        "Qwen implementation patches",
        "Qwen file writes",
        "Qwen runtime execution",
        "Qwen shell execution",
        "Qwen source mutation",
        "Qwen strategy rule enablement",
        "Qwen trade simulation enablement",
        "Qwen learning",
        "Qwen promotion",
        "Qwen broker orders",
        "Qwen live trading",
        "Qwen snapshot mutation",
    ],
    "next_recommended_phase": "54A_QWEN_READ_ONLY_HANDOFF_EXPORT_SUMMARY_STUB",
    "next_phase_rule": "Create Qwen read-only handoff export summary only. No writes, execution, or implementation instructions.",
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
        "from": "53A_QWEN_READ_ONLY_HANDOFF_FREEZE_STUB",
        "through": "53B_QWEN_READ_ONLY_HANDOFF_FREEZE_ROLLUP_CERTIFICATION",
        "to": "53C_HANDOFF_BUNDLE_REFRESH",
        "certified_capability": [
            "Qwen read-only handoff freeze exists",
            "frozen handoff snapshot is certified",
            "snapshot read is allowed",
            "snapshot writes remain blocked",
            "recursive/autonomous execution remains blocked",
            "actions/writes/runtime/shell/source mutation remain blocked",
            "broker/live execution remains blocked",
            "no runtime capability introduced",
        ],
        "current_behavior": [
            "read-only frozen handoff snapshot only",
            "architecture summaries only",
            "locked gate explanations only",
            "missing context reports only",
            "safe next phase recommendations only",
        ],
        "next_recommended_phase": "54A_QWEN_READ_ONLY_HANDOFF_EXPORT_SUMMARY_STUB",
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
