from __future__ import annotations

from typing import Any

from backend.app.stacks.strategy_candidate_sandbox.trade_simulation_contract import SAFETY_LOCKS


ENABLEMENT_GATE_KEYS = [
    "gate_id",
    "candidate_id",
    "symbol",
    "requested_rule_type",
    "requested_action",
    "manual_approval_required",
    "manual_approval_present",
    "metrics_required",
    "metrics_certified",
    "scorecard_required",
    "scorecard_certified",
    "promotion_gate_required",
    "promotion_gate_passed",
    "rule_enablement_allowed",
    "entry_rules_enabled",
    "exit_rules_enabled",
    "trade_simulation_enabled",
]


def build_locked_enablement_gate(candidate_id: str, symbol: str, requested_rule_type: str) -> dict[str, Any]:
    return {
        "gate_id": "strategy_rule_enablement_gate_001",
        "candidate_id": candidate_id,
        "symbol": symbol,
        "requested_rule_type": requested_rule_type,
        "requested_action": "enable_strategy_rule",
        "manual_approval_required": True,
        "manual_approval_present": False,
        "metrics_required": True,
        "metrics_certified": False,
        "scorecard_required": True,
        "scorecard_certified": False,
        "promotion_gate_required": True,
        "promotion_gate_passed": False,
        "rule_enablement_allowed": False,
        "entry_rules_enabled": False,
        "exit_rules_enabled": False,
        "trade_simulation_enabled": False,
        "learning_enabled": False,
        "promotion_enabled": False,
        "registry_write_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
        "safety_locks": SAFETY_LOCKS.copy(),
    }


def validate_locked_enablement_gate(gate: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "gate_is_dict": isinstance(gate, dict),
        "all_gate_keys_present": isinstance(gate, dict) and all(k in gate for k in ENABLEMENT_GATE_KEYS),
        "manual_approval_required": isinstance(gate, dict) and gate.get("manual_approval_required") is True,
        "manual_approval_absent": isinstance(gate, dict) and gate.get("manual_approval_present") is False,
        "metrics_not_certified": isinstance(gate, dict) and gate.get("metrics_certified") is False,
        "scorecard_not_certified": isinstance(gate, dict) and gate.get("scorecard_certified") is False,
        "promotion_gate_not_passed": isinstance(gate, dict) and gate.get("promotion_gate_passed") is False,
        "rule_enablement_not_allowed": isinstance(gate, dict) and gate.get("rule_enablement_allowed") is False,
        "entry_rules_disabled": isinstance(gate, dict) and gate.get("entry_rules_enabled") is False,
        "exit_rules_disabled": isinstance(gate, dict) and gate.get("exit_rules_enabled") is False,
        "trade_simulation_disabled": isinstance(gate, dict) and gate.get("trade_simulation_enabled") is False,
        "learning_disabled": isinstance(gate, dict) and gate.get("learning_enabled") is False,
        "promotion_disabled": isinstance(gate, dict) and gate.get("promotion_enabled") is False,
        "registry_write_disabled": isinstance(gate, dict) and gate.get("registry_write_enabled") is False,
        "broker_execution_disabled": isinstance(gate, dict) and gate.get("broker_execution_enabled") is False,
        "live_execution_disabled": isinstance(gate, dict) and gate.get("live_execution_enabled") is False,
        "all_safety_locks_false": isinstance(gate, dict) and all(v is False for v in gate.get("safety_locks", {}).values()),
    }

    return {
        "status": "ok" if all(checks.values()) else "failed",
        "checks": checks,
        "certified": all(checks.values()),
    }
