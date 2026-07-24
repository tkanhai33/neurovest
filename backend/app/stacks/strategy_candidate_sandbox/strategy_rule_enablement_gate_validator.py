from __future__ import annotations

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
