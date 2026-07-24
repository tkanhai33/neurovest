#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX_DIR = ROOT / "backend/app/stacks/strategy_candidate_sandbox"
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)

VALIDATOR = SANDBOX_DIR / "strategy_rule_enablement_gate_validator.py"
OUT_DIR = ROOT / "runtime/strategy_candidate_sandbox"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT = OUT_DIR / "36B_enablement_gate_validation_stub_latest.json"

PHASE = "36B_ENABLEMENT_GATE_VALIDATION_STUB"

VALIDATOR.write_text('''from __future__ import annotations

from typing import Any

from backend.app.stacks.strategy_candidate_sandbox.strategy_rule_enablement_gate_contract import (
    validate_locked_enablement_gate,
)
from backend.app.stacks.strategy_candidate_sandbox.trade_simulation_contract import SAFETY_LOCKS


def validate_gate_locked_state(gate: dict[str, Any]) -> dict[str, Any]:
    base = validate_locked_enablement_gate(gate)

    checks = {
        "base_gate_certified": base.get("certified") is True,
        "rule_enablement_not_allowed": isinstance(gate, dict) and gate.get("rule_enablement_allowed") is False,
        "entry_rules_disabled": isinstance(gate, dict) and gate.get("entry_rules_enabled") is False,
        "exit_rules_disabled": isinstance(gate, dict) and gate.get("exit_rules_enabled") is False,
        "trade_simulation_disabled": isinstance(gate, dict) and gate.get("trade_simulation_enabled") is False,
        "broker_execution_disabled": isinstance(gate, dict) and gate.get("broker_execution_enabled") is False,
        "live_execution_disabled": isinstance(gate, dict) and gate.get("live_execution_enabled") is False,
        "all_safety_locks_false": isinstance(gate, dict) and all(v is False for v in gate.get("safety_locks", {}).values()),
    }

    return {
        "status": "ok" if all(checks.values()) else "failed",
        "checks": checks,
        "certified": all(checks.values()),
        "safety_locks": SAFETY_LOCKS.copy(),
    }


def validate_unsafe_enabled_gate_is_rejected(gate: dict[str, Any]) -> dict[str, Any]:
    unsafe = dict(gate)
    unsafe["manual_approval_present"] = True
    unsafe["metrics_certified"] = True
    unsafe["scorecard_certified"] = True
    unsafe["promotion_gate_passed"] = True
    unsafe["rule_enablement_allowed"] = True
    unsafe["entry_rules_enabled"] = True
    unsafe["exit_rules_enabled"] = True
    unsafe["trade_simulation_enabled"] = True

    validation = validate_gate_locked_state(unsafe)

    checks = {
        "unsafe_gate_rejected": validation.get("certified") is False,
        "rule_enablement_true_detected": unsafe.get("rule_enablement_allowed") is True,
        "entry_enabled_true_detected": unsafe.get("entry_rules_enabled") is True,
        "exit_enabled_true_detected": unsafe.get("exit_rules_enabled") is True,
        "trade_simulation_true_detected": unsafe.get("trade_simulation_enabled") is True,
        "safety_locks_still_false": all(v is False for v in SAFETY_LOCKS.values()),
    }

    return {
        "status": "ok" if all(checks.values()) else "failed",
        "checks": checks,
        "certified": all(checks.values()),
        "unsafe_validation": validation,
        "safety_locks": SAFETY_LOCKS.copy(),
    }
''', encoding="utf-8")

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "created_file": str(VALIDATOR),
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    import py_compile
    py_compile.compile(str(VALIDATOR), doraise=True)

    from backend.app.stacks.strategy_candidate_sandbox.strategy_rule_enablement_gate_contract import (
        build_locked_enablement_gate,
    )
    from backend.app.stacks.strategy_candidate_sandbox.strategy_rule_enablement_gate_validator import (
        validate_gate_locked_state,
        validate_unsafe_enabled_gate_is_rejected,
    )

    gate = build_locked_enablement_gate("candidate_31e_stub_001", "AAPL", "entry_or_exit_rule")
    locked_validation = validate_gate_locked_state(gate)
    unsafe_rejection = validate_unsafe_enabled_gate_is_rejected(gate)

    result["sample_gate"] = gate
    result["locked_validation"] = locked_validation
    result["unsafe_rejection"] = unsafe_rejection

    result["checks"]["validator_file_exists"] = VALIDATOR.exists()
    result["checks"]["validator_compiles"] = True
    result["checks"]["locked_validation_certified"] = locked_validation.get("certified") is True
    result["checks"]["unsafe_enabled_gate_rejected"] = unsafe_rejection.get("certified") is True
    result["checks"]["rule_enablement_not_allowed"] = gate.get("rule_enablement_allowed") is False
    result["checks"]["entry_rules_disabled"] = gate.get("entry_rules_enabled") is False
    result["checks"]["exit_rules_disabled"] = gate.get("exit_rules_enabled") is False
    result["checks"]["trade_simulation_disabled"] = gate.get("trade_simulation_enabled") is False
    result["checks"]["broker_execution_disabled"] = gate.get("broker_execution_enabled") is False
    result["checks"]["live_execution_disabled"] = gate.get("live_execution_enabled") is False
    result["checks"]["all_safety_locks_false"] = all(v is False for v in gate.get("safety_locks", {}).values())

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(json.dumps(result, indent=2))
print(f"\nWROTE: {OUT}")
