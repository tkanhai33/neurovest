from __future__ import annotations

from typing import Any

from backend.app.stacks.strategy_candidate_sandbox.trade_simulation_contract import SAFETY_LOCKS
from backend.app.stacks.strategy_candidate_sandbox.exit_signal_rule_validator import validate_disabled_exit_rule


def generate_exit_signals_disabled(
    candidate_id: str,
    symbol: str,
    bars: list[dict[str, Any]],
    rule: dict[str, Any],
) -> dict[str, Any]:
    rule_validation = validate_disabled_exit_rule(rule)

    return {
        "status": "exit_signal_generator_disabled_stub",
        "candidate_id": candidate_id,
        "symbol": symbol,
        "bars_input": len(bars) if isinstance(bars, list) else 0,
        "rule_validated": rule_validation.get("certified") is True,
        "rule_enabled": rule.get("enabled") if isinstance(rule, dict) else None,
        "exit_signal_generation_enabled": rule.get("exit_signal_generation_enabled") if isinstance(rule, dict) else None,
        "strategy_logic_enabled": rule.get("strategy_logic_enabled") if isinstance(rule, dict) else None,
        "exit_signals_created": 0,
        "signals": [],
        "entry_signals_created": 0,
        "hold_signals_created": 0,
        "trade_events_created": 0,
        "trades_simulated": 0,
        "broker_orders_created": 0,
        "live_orders_created": 0,
        "metrics_generated": False,
        "scorecard_generated": False,
        "registry_written": False,
        "promotion_attempted": False,
        "learning_attempted": False,
        "rule_validation": rule_validation,
        "safety_locks": SAFETY_LOCKS.copy(),
    }


def validate_exit_signal_generator_disabled(payload: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "payload_is_dict": isinstance(payload, dict),
        "status_ok": payload.get("status") == "exit_signal_generator_disabled_stub",
        "bars_input_gt_zero": payload.get("bars_input", 0) > 0,
        "rule_validated": payload.get("rule_validated") is True,
        "rule_enabled_false": payload.get("rule_enabled") is False,
        "exit_generation_disabled": payload.get("exit_signal_generation_enabled") is False,
        "strategy_logic_disabled": payload.get("strategy_logic_enabled") is False,
        "exit_signals_zero": payload.get("exit_signals_created") == 0,
        "signals_empty": payload.get("signals") == [],
        "entry_signals_zero": payload.get("entry_signals_created") == 0,
        "trade_events_zero": payload.get("trade_events_created") == 0,
        "trades_simulated_zero": payload.get("trades_simulated") == 0,
        "broker_orders_zero": payload.get("broker_orders_created") == 0,
        "live_orders_zero": payload.get("live_orders_created") == 0,
        "metrics_not_generated": payload.get("metrics_generated") is False,
        "scorecard_not_generated": payload.get("scorecard_generated") is False,
        "registry_not_written": payload.get("registry_written") is False,
        "promotion_not_attempted": payload.get("promotion_attempted") is False,
        "learning_not_attempted": payload.get("learning_attempted") is False,
        "all_safety_locks_false": all(v is False for v in payload.get("safety_locks", {}).values()),
    }

    return {
        "status": "ok" if all(checks.values()) else "failed",
        "checks": checks,
        "certified": all(checks.values()),
    }
