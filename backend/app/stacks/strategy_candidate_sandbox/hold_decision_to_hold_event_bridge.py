from __future__ import annotations

from typing import Any

from backend.app.stacks.strategy_candidate_sandbox.trade_simulation_contract import SAFETY_LOCKS
from backend.app.stacks.strategy_candidate_sandbox.trade_event_validator import validate_trade_event_shape


def bridge_hold_decisions_to_events(decisions: list[dict[str, Any]]) -> dict[str, Any]:
    events = []
    validations = []

    if isinstance(decisions, list):
        for index, decision in enumerate(decisions):
            if not isinstance(decision, dict):
                continue
            if decision.get("decision") != "hold":
                continue

            event = {
                "event_id": f"bridged_hold_event_{index:06d}",
                "candidate_id": decision.get("candidate_id"),
                "symbol": decision.get("symbol"),
                "timestamp": decision.get("timestamp"),
                "side": "hold",
                "quantity": 0,
                "price": 0.0,
                "reason": "33G_hold_decision_bridge_no_trade_execution",
                "source": "33G_hold_decision_to_hold_event_bridge",
                "simulated": False,
                "broker_order_created": False,
                "live_order_created": False,
            }

            validation = validate_trade_event_shape(event)

            if validation.get("certified") is True:
                events.append(event)

            validations.append(validation)

    return {
        "status": "hold_decisions_bridged_to_hold_events",
        "decisions_input": len(decisions) if isinstance(decisions, list) else 0,
        "hold_events_created": len(events),
        "events": events,
        "validation_count": len(validations),
        "all_events_valid": all(v.get("certified") is True for v in validations) if validations else False,
        "entry_events_created": 0,
        "exit_events_created": 0,
        "trades_simulated": 0,
        "entries": 0,
        "exits": 0,
        "broker_orders_created": 0,
        "live_orders_created": 0,
        "simulation_enabled": False,
        "strategy_logic_enabled": False,
        "metrics_generated": False,
        "scorecard_generated": False,
        "registry_written": False,
        "promotion_attempted": False,
        "learning_attempted": False,
        "safety_locks": SAFETY_LOCKS.copy(),
    }


def validate_hold_decision_bridge(payload: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "payload_is_dict": isinstance(payload, dict),
        "status_ok": payload.get("status") == "hold_decisions_bridged_to_hold_events",
        "hold_events_created_gt_zero": payload.get("hold_events_created", 0) > 0,
        "hold_events_match_decisions": payload.get("hold_events_created") == payload.get("decisions_input"),
        "all_events_valid": payload.get("all_events_valid") is True,
        "entry_events_zero": payload.get("entry_events_created") == 0,
        "exit_events_zero": payload.get("exit_events_created") == 0,
        "trades_simulated_zero": payload.get("trades_simulated") == 0,
        "entries_zero": payload.get("entries") == 0,
        "exits_zero": payload.get("exits") == 0,
        "broker_orders_zero": payload.get("broker_orders_created") == 0,
        "live_orders_zero": payload.get("live_orders_created") == 0,
        "simulation_disabled": payload.get("simulation_enabled") is False,
        "strategy_logic_disabled": payload.get("strategy_logic_enabled") is False,
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
