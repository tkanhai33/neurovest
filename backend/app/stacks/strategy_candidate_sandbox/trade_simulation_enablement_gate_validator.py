from __future__ import annotations

from typing import Any

from backend.app.stacks.strategy_candidate_sandbox.trade_simulation_enablement_gate_contract import (
    validate_locked_trade_simulation_gate,
)

from backend.app.stacks.strategy_candidate_sandbox.trade_simulation_contract import SAFETY_LOCKS


def validate_trade_simulation_gate_locked(
    gate: dict[str, Any],
) -> dict[str, Any]:

    base = validate_locked_trade_simulation_gate(gate)

    checks = {
        "base_gate_certified": base.get("certified") is True,
        "trade_simulation_not_allowed": gate.get("trade_simulation_allowed") is False,
        "trade_simulation_disabled": gate.get("trade_simulation_enabled") is False,
        "entry_rules_disabled": gate.get("entry_rules_enabled") is False,
        "exit_rules_disabled": gate.get("exit_rules_enabled") is False,
        "trade_events_zero": gate.get("trade_events_created") == 0,
        "trades_simulated_zero": gate.get("trades_simulated") == 0,
        "metrics_not_generated": gate.get("metrics_generated") is False,
        "scorecard_not_generated": gate.get("scorecard_generated") is False,
        "registry_write_disabled": gate.get("registry_write_enabled") is False,
        "learning_disabled": gate.get("learning_enabled") is False,
        "promotion_disabled": gate.get("promotion_enabled") is False,
        "broker_execution_disabled": gate.get("broker_execution_enabled") is False,
        "live_execution_disabled": gate.get("live_execution_enabled") is False,
        "all_safety_locks_false": all(
            v is False for v in gate.get("safety_locks", {}).values()
        ),
    }

    return {
        "status": "ok" if all(checks.values()) else "failed",
        "checks": checks,
        "certified": all(checks.values()),
        "safety_locks": SAFETY_LOCKS.copy(),
    }


def validate_unsafe_trade_simulation_gate_is_rejected(
    gate: dict[str, Any],
) -> dict[str, Any]:

    unsafe = dict(gate)

    unsafe["manual_approval_present"] = True
    unsafe["entry_rules_enabled"] = True
    unsafe["exit_rules_enabled"] = True
    unsafe["risk_gate_passed"] = True
    unsafe["trade_simulation_allowed"] = True
    unsafe["trade_simulation_enabled"] = True

    validation = validate_trade_simulation_gate_locked(unsafe)

    checks = {
        "unsafe_gate_rejected": validation.get("certified") is False,
        "trade_simulation_true_detected": unsafe.get("trade_simulation_enabled") is True,
        "trade_simulation_allowed_detected": unsafe.get("trade_simulation_allowed") is True,
        "entry_rules_true_detected": unsafe.get("entry_rules_enabled") is True,
        "exit_rules_true_detected": unsafe.get("exit_rules_enabled") is True,
        "risk_gate_true_detected": unsafe.get("risk_gate_passed") is True,
        "safety_locks_still_false": all(
            v is False for v in SAFETY_LOCKS.values()
        ),
    }

    return {
        "status": "ok" if all(checks.values()) else "failed",
        "checks": checks,
        "certified": all(checks.values()),
        "unsafe_validation": validation,
        "safety_locks": SAFETY_LOCKS.copy(),
    }
