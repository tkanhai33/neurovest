#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "53B_qwen_read_only_handoff_freeze_rollup_certification_latest.json"
PHASE = "53B_QWEN_READ_ONLY_HANDOFF_FREEZE_ROLLUP_CERTIFICATION"

ARTIFACT = SANDBOX / "53A_qwen_read_only_handoff_freeze_stub_latest.json"

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
    freeze = data.get("freeze_payload", {}) if isinstance(data.get("freeze_payload"), dict) else {}
    snapshot = freeze.get("snapshot_fields", {}) if isinstance(freeze.get("snapshot_fields"), dict) else {}

    result["source_phase"] = data.get("phase")
    result["source_certified"] = data.get("certified") is True

    result["freeze_summary"] = {
        "status": freeze.get("status"),
        "freeze_mode": freeze.get("freeze_mode"),
        "stage": snapshot.get("stage"),
        "latest_confirmed_phase": snapshot.get("latest_confirmed_phase"),
        "next_recommended_phase": freeze.get("recommended_next_read_only_phase"),
    }

    result["checks"]["artifact_exists"] = ARTIFACT.exists()
    result["checks"]["source_certified"] = data.get("certified") is True
    result["checks"]["status_ok"] = freeze.get("status") == "qwen_read_only_handoff_freeze_ready"
    result["checks"]["freeze_mode_read_only"] = freeze.get("freeze_mode") == "read_only_handoff_snapshot_only"
    result["checks"]["handoff_certified"] = freeze.get("handoff_certified") is True
    result["checks"]["snapshot_fields_present"] = len(snapshot) > 0
    result["checks"]["snapshot_read_allowed"] = freeze.get("snapshot_read_allowed") is True
    result["checks"]["snapshot_write_blocked"] = freeze.get("snapshot_write_allowed") is False
    result["checks"]["actions_not_allowed"] = freeze.get("actions_allowed") is False
    result["checks"]["writes_not_allowed"] = freeze.get("writes_allowed") is False
    result["checks"]["runtime_not_allowed"] = freeze.get("runtime_allowed") is False
    result["checks"]["shell_execution_not_allowed"] = freeze.get("shell_execution_allowed") is False
    result["checks"]["source_mutation_not_allowed"] = freeze.get("source_mutation_allowed") is False
    result["checks"]["broker_or_live_not_allowed"] = freeze.get("broker_or_live_allowed") is False
    result["checks"]["recursive_execution_not_allowed"] = freeze.get("recursive_execution_allowed") is False
    result["checks"]["autonomous_phase_execution_not_allowed"] = freeze.get("autonomous_phase_execution_allowed") is False
    result["checks"]["critical_safety_locks_false"] = all(
        value is False
        for value in snapshot.get("critical_safety_locks", {}).values()
    )
    result["checks"]["has_next_read_only_phase"] = bool(freeze.get("recommended_next_read_only_phase"))

    result["pipeline_summary"] = {
        "from": "53A_QWEN_READ_ONLY_HANDOFF_FREEZE_STUB",
        "to": "53B_QWEN_READ_ONLY_HANDOFF_FREEZE_ROLLUP_CERTIFICATION",
        "certified_capability": [
            "Qwen read-only handoff freeze exists",
            "handoff snapshot fields are present",
            "snapshot read is allowed",
            "snapshot writes remain blocked",
            "actions/writes/runtime/shell/source mutation remain blocked",
            "broker/live execution remains blocked",
            "recursive/autonomous execution remains blocked",
            "critical safety locks remain false",
        ],
        "current_behavior": [
            "Qwen may read frozen handoff snapshot only",
            "Qwen may summarize frozen read-only state",
            "Qwen may not mutate the frozen snapshot",
            "Qwen may not execute from the frozen snapshot",
        ],
        "next_recommended_phase": "53C_HANDOFF_BUNDLE_REFRESH",
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
