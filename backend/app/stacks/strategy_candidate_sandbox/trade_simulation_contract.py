from __future__ import annotations

from typing import Any


SAFETY_LOCKS = {
    "live_execution_enabled": False,
    "broker_execution_enabled": False,
    "historical_replay_enabled": False,
    "simulation_enabled": False,
    "registry_write_enabled": False,
    "promotion_enabled": False,
    "learning_enabled": False,
}


TRADE_EVENT_CONTRACT_KEYS = [
    "event_id",
    "candidate_id",
    "symbol",
    "timestamp",
    "side",
    "quantity",
    "price",
    "reason",
    "source",
    "simulated",
    "broker_order_created",
    "live_order_created",
]


def build_empty_trade_simulation_contract(candidate_id: str, symbol: str) -> dict[str, Any]:
    return {
        "candidate_id": candidate_id,
        "symbol": symbol,
        "status": "contract_stub_only",
        "simulation_enabled": False,
        "trade_events": [],
        "trade_event_contract_keys": TRADE_EVENT_CONTRACT_KEYS.copy(),
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


def validate_trade_simulation_contract(payload: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "payload_is_dict": isinstance(payload, dict),
        "status_contract_stub_only": payload.get("status") == "contract_stub_only",
        "simulation_enabled_false": payload.get("simulation_enabled") is False,
        "trade_events_empty": payload.get("trade_events") == [],
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
