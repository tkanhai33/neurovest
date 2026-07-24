from __future__ import annotations

from typing import Any

from backend.app.stacks.strategy_candidate_sandbox.trade_simulation_contract import SAFETY_LOCKS


ENTRY_RULE_CONTRACT_KEYS = [
    "rule_id",
    "candidate_id",
    "symbol",
    "rule_type",
    "enabled",
    "lookback_bars",
    "threshold",
    "confidence_floor",
    "reason",
    "source",
    "strategy_logic_enabled",
    "entry_signal_generation_enabled",
    "trade_event_created",
]


VALID_ENTRY_RULE_TYPES = {
    "momentum_stub",
    "mean_reversion_stub",
    "breakout_stub",
    "disabled_stub",
}


def build_disabled_entry_rule_contract(candidate_id: str, symbol: str) -> dict[str, Any]:
    return {
        "rule_id": "disabled_entry_rule_001",
        "candidate_id": candidate_id,
        "symbol": symbol,
        "rule_type": "disabled_stub",
        "enabled": False,
        "lookback_bars": 0,
        "threshold": None,
        "confidence_floor": 0.0,
        "reason": "34A_contract_only_no_entry_signal_generation",
        "source": "34A_entry_signal_rule_contract_stub",
        "strategy_logic_enabled": False,
        "entry_signal_generation_enabled": False,
        "trade_event_created": False,
        "safety_locks": SAFETY_LOCKS.copy(),
    }


def validate_entry_rule_contract(rule: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "rule_is_dict": isinstance(rule, dict),
        "all_contract_keys_present": isinstance(rule, dict) and all(k in rule for k in ENTRY_RULE_CONTRACT_KEYS),
        "rule_type_valid": isinstance(rule, dict) and rule.get("rule_type") in VALID_ENTRY_RULE_TYPES,
        "enabled_false": isinstance(rule, dict) and rule.get("enabled") is False,
        "lookback_bars_zero": isinstance(rule, dict) and rule.get("lookback_bars") == 0,
        "confidence_floor_zero": isinstance(rule, dict) and rule.get("confidence_floor") == 0.0,
        "strategy_logic_disabled": isinstance(rule, dict) and rule.get("strategy_logic_enabled") is False,
        "entry_signal_generation_disabled": isinstance(rule, dict) and rule.get("entry_signal_generation_enabled") is False,
        "trade_event_not_created": isinstance(rule, dict) and rule.get("trade_event_created") is False,
        "all_safety_locks_false": isinstance(rule, dict) and all(v is False for v in rule.get("safety_locks", {}).values()),
    }

    return {
        "status": "ok" if all(checks.values()) else "failed",
        "checks": checks,
        "certified": all(checks.values()),
    }
