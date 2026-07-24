#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "60B_qwen_read_only_terminal_freeze_rollup_certification_latest.json"
PHASE = "60B_QWEN_READ_ONLY_TERMINAL_FREEZE_ROLLUP_CERTIFICATION"

ARTIFACT = SANDBOX / "60A_qwen_read_only_terminal_freeze_stub_latest.json"

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

    freeze = (
        data.get("terminal_freeze_payload", {})
        if isinstance(data.get("terminal_freeze_payload"), dict)
        else {}
    )

    snapshot = (
        freeze.get("terminal_snapshot", {})
        if isinstance(freeze.get("terminal_snapshot"), dict)
        else {}
    )

    result["source_phase"] = data.get("phase")
    result["source_certified"] = data.get("certified") is True

    result["terminal_freeze_summary"] = {
        "status": freeze.get("status"),
        "freeze_mode": freeze.get("freeze_mode"),
        "stage": snapshot.get("stage"),
        "latest_confirmed_phase": snapshot.get("latest_confirmed_phase"),
        "recommended_next_read_only_phase": freeze.get("recommended_next_read_only_phase"),
    }

    result["checks"]["artifact_exists"] = ARTIFACT.exists()
    result["checks"]["source_certified"] = data.get("certified") is True
    result["checks"]["status_ok"] = freeze.get("status") == "qwen_read_only_terminal_freeze_ready"
    result["checks"]["mode_terminal_read_only"] = freeze.get("freeze_mode") == "terminal_read_only_no_next_execution"
    result["checks"]["handoff_certified"] = freeze.get("handoff_certified") is True
    result["checks"]["snapshot_present"] = len(snapshot) > 0

    result["checks"]["terminal_read_allowed"] = freeze.get("terminal_read_allowed") is True
    result["checks"]["terminal_write_blocked"] = freeze.get("terminal_write_allowed") is False
    result["checks"]["terminal_execution_blocked"] = freeze.get("terminal_execution_allowed") is False
    result["checks"]["terminal_mutation_blocked"] = freeze.get("terminal_mutation_allowed") is False
    result["checks"]["terminal_next_phase_generation_blocked"] = freeze.get("terminal_next_phase_generation_allowed") is False

    result["checks"]["actions_blocked"] = freeze.get("actions_allowed") is False
    result["checks"]["writes_blocked"] = freeze.get("writes_allowed") is False
    result["checks"]["runtime_blocked"] = freeze.get("runtime_allowed") is False
    result["checks"]["shell_execution_blocked"] = freeze.get("shell_execution_allowed") is False
    result["checks"]["source_mutation_blocked"] = freeze.get("source_mutation_allowed") is False
    result["checks"]["policy_mutation_blocked"] = freeze.get("policy_mutation_allowed") is False
    result["checks"]["matrix_mutation_blocked"] = freeze.get("matrix_mutation_allowed") is False
    result["checks"]["handoff_mutation_blocked"] = freeze.get("handoff_mutation_allowed") is False
    result["checks"]["broker_or_live_blocked"] = freeze.get("broker_or_live_allowed") is False
    result["checks"]["recursive_execution_blocked"] = freeze.get("recursive_execution_allowed") is False
    result["checks"]["autonomous_phase_execution_blocked"] = freeze.get("autonomous_phase_execution_allowed") is False

    result["checks"]["critical_safety_locks_false"] = all(
        value is False
        for value in snapshot.get("critical_safety_locks", {}).values()
    )

    result["checks"]["has_next_read_only_phase"] = bool(
        freeze.get("recommended_next_read_only_phase")
    )

    result["pipeline_summary"] = {
        "from": "60A_QWEN_READ_ONLY_TERMINAL_FREEZE_STUB",
        "to": "60B_QWEN_READ_ONLY_TERMINAL_FREEZE_ROLLUP_CERTIFICATION",
        "certified_capability": [
            "Qwen terminal read-only freeze exists",
            "terminal snapshot is present",
            "terminal read is allowed",
            "terminal write/execution/mutation are blocked",
            "terminal next phase generation is blocked",
            "runtime/shell/source/policy/matrix/handoff mutation remain blocked",
            "broker/live and recursive/autonomous execution remain blocked",
            "critical safety locks remain false",
        ],
        "current_behavior": [
            "Qwen may inspect terminal read-only snapshot only",
            "Qwen may summarize terminal read-only state",
            "Qwen may not generate execution or mutation paths",
            "Qwen may not advance phases autonomously",
        ],
        "next_recommended_phase": "60C_HANDOFF_BUNDLE_REFRESH",
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
