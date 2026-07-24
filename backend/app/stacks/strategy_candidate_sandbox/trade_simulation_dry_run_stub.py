from __future__ import annotations

from typing import Any

from backend.app.stacks.strategy_candidate_sandbox.trade_simulation_contract import SAFETY_LOCKS
from backend.app.stacks.strategy_candidate_sandbox.trade_event_validator import validate_trade_event_shape


def build_hold_event(candidate_id: str, symbol: str, bar: dict[str, Any], index: int) -> dict[str, Any]:
    return {
        "event_id": f"hold_event_{index:06d}",
        "candidate_id": candidate_id,
        "symbol": symbol,
        "timestamp": bar.get("timestamp"),
        "side": "hold",
        "quantity": 0,
        "price": float(bar.get("close")),
        "reason": "33C_hold_only_dry_run_no_trade_logic",
        "source": "33C_trade_simulation_dry_run_stub",
        "simulated": False,
        "broker_order_created": False,
        "live_order_created": False,
    }


def run_hold_only_trade_simulation_dry_run(
    candidate_id: str,
    symbol: str,
    bars: list[dict[str, Any]],
) -> dict[str, Any]:
    events = []
    validation_results = []

    if isinstance(bars, list):
        for index, bar in enumerate(bars):
            if not isinstance(bar, dict):
                continue
            if "timestamp" not in bar or "close" not in bar:
                continue

            event = build_hold_event(candidate_id, symbol, bar, index)
            validation = validate_trade_event_shape(event)

            if validation.get("certified") is True:
                events.append(event)

            validation_results.append(validation)

    return {
        "status": "hold_only_dry_run_complete",
        "candidate_id": candidate_id,
        "symbol": symbol,
        "simulation_enabled": False,
        "bars_input": len(bars) if isinstance(bars, list) else 0,
        "hold_events_created": len(events),
        "trade_events": events,
        "validation_count": len(validation_results),
        "all_events_valid": all(v.get("certified") is True for v in validation_results) if validation_results else False,
        "trades_simulated": 0,
        "entries": 0,
        "exits": 0,
        "broker_orders_created": 0,
        "live_orders_created": 0,
        "metrics_generated": False,
        "scorecard_generated": False,
        "registry_written": False,
        "promotion_attempted": False,
        "learning_attempted": False,
        "safety_locks": SAFETY_LOCKS.copy(),
    }


def validate_hold_only_dry_run(payload: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "payload_is_dict": isinstance(payload, dict),
        "status_complete": payload.get("status") == "hold_only_dry_run_complete",
        "simulation_enabled_false": payload.get("simulation_enabled") is False,
        "hold_events_created_gt_zero": payload.get("hold_events_created", 0) > 0,
        "hold_events_match_bars_input": payload.get("hold_events_created") == payload.get("bars_input"),
        "all_events_valid": payload.get("all_events_valid") is True,
        "trades_simulated_zero": payload.get("trades_simulated") == 0,
        "entries_zero": payload.get("entries") == 0,
        "exits_zero": payload.get("exits") == 0,
        "broker_orders_created_zero": payload.get("broker_orders_created") == 0,
        "live_orders_created_zero": payload.get("live_orders_created") == 0,
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
