#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "60A_qwen_read_only_terminal_freeze_stub_latest.json"
PHASE = "60A_QWEN_READ_ONLY_TERMINAL_FREEZE_STUB"

HANDOFF = SANDBOX / "59C_handoff_bundle_refresh_latest.json"

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
    snapshot = handoff.get("handoff_snapshot", {}) if isinstance(handoff.get("handoff_snapshot"), dict) else {}

    terminal_freeze = {
        "status": "qwen_read_only_terminal_freeze_ready",
        "freeze_mode": "terminal_read_only_no_next_execution",
        "handoff_certified": handoff.get("certified") is True,

        "terminal_snapshot": {
            "stage": snapshot.get("stage"),
            "latest_confirmed_phase": snapshot.get("latest_confirmed_phase"),
            "current_capabilities": snapshot.get("current_capabilities", []),
            "still_disabled": snapshot.get("still_disabled", []),
            "critical_safety_locks": snapshot.get("critical_safety_locks", {}),
        },

        "terminal_read_allowed": True,
        "terminal_write_allowed": False,
        "terminal_execution_allowed": False,
        "terminal_mutation_allowed": False,
        "terminal_next_phase_generation_allowed": False,

        "actions_allowed": False,
        "writes_allowed": False,
        "runtime_allowed": False,
        "shell_execution_allowed": False,
        "source_mutation_allowed": False,
        "policy_mutation_allowed": False,
        "matrix_mutation_allowed": False,
        "handoff_mutation_allowed": False,
        "broker_or_live_allowed": False,
        "recursive_execution_allowed": False,
        "autonomous_phase_execution_allowed": False,

        "recommended_next_read_only_phase":
            "60B_QWEN_READ_ONLY_TERMINAL_FREEZE_ROLLUP_CERTIFICATION",
    }

    result["terminal_freeze_payload"] = terminal_freeze

    result["checks"]["handoff_exists"] = HANDOFF.exists()
    result["checks"]["handoff_certified"] = handoff.get("certified") is True
    result["checks"]["status_ok"] = terminal_freeze["status"] == "qwen_read_only_terminal_freeze_ready"
    result["checks"]["mode_terminal_read_only"] = terminal_freeze["freeze_mode"] == "terminal_read_only_no_next_execution"
    result["checks"]["snapshot_present"] = len(terminal_freeze["terminal_snapshot"]) > 0
    result["checks"]["terminal_read_allowed"] = terminal_freeze["terminal_read_allowed"] is True
    result["checks"]["terminal_write_blocked"] = terminal_freeze["terminal_write_allowed"] is False
    result["checks"]["terminal_execution_blocked"] = terminal_freeze["terminal_execution_allowed"] is False
    result["checks"]["terminal_mutation_blocked"] = terminal_freeze["terminal_mutation_allowed"] is False
    result["checks"]["terminal_next_phase_generation_blocked"] = terminal_freeze["terminal_next_phase_generation_allowed"] is False
    result["checks"]["actions_blocked"] = terminal_freeze["actions_allowed"] is False
    result["checks"]["writes_blocked"] = terminal_freeze["writes_allowed"] is False
    result["checks"]["runtime_blocked"] = terminal_freeze["runtime_allowed"] is False
    result["checks"]["shell_execution_blocked"] = terminal_freeze["shell_execution_allowed"] is False
    result["checks"]["source_mutation_blocked"] = terminal_freeze["source_mutation_allowed"] is False
    result["checks"]["policy_mutation_blocked"] = terminal_freeze["policy_mutation_allowed"] is False
    result["checks"]["matrix_mutation_blocked"] = terminal_freeze["matrix_mutation_allowed"] is False
    result["checks"]["handoff_mutation_blocked"] = terminal_freeze["handoff_mutation_allowed"] is False
    result["checks"]["broker_or_live_blocked"] = terminal_freeze["broker_or_live_allowed"] is False
    result["checks"]["recursive_execution_blocked"] = terminal_freeze["recursive_execution_allowed"] is False
    result["checks"]["autonomous_phase_execution_blocked"] = terminal_freeze["autonomous_phase_execution_allowed"] is False
    result["checks"]["critical_safety_locks_false"] = all(
        value is False
        for value in terminal_freeze["terminal_snapshot"].get("critical_safety_locks", {}).values()
    )
    result["checks"]["has_rollup_phase"] = bool(terminal_freeze["recommended_next_read_only_phase"])

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(json.dumps(result, indent=2))
print(f"\nWROTE: {OUT}")
