from __future__ import annotations

from typing import Any

from backend.app.stacks.strategy_candidate_sandbox.trade_simulation_contract import (
    TRADE_EVENT_CONTRACT_KEYS,
    SAFETY_LOCKS,
)


VALID_SIDES = {"entry", "exit", "hold"}


def validate_trade_event_shape(event: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "event_is_dict": isinstance(event, dict),
        "all_contract_keys_present": isinstance(event, dict) and all(k in event for k in TRADE_EVENT_CONTRACT_KEYS),
        "side_valid": isinstance(event, dict) and event.get("side") in VALID_SIDES,
        "quantity_numeric_or_zero": isinstance(event, dict) and isinstance(event.get("quantity"), (int, float)) and not isinstance(event.get("quantity"), bool),
        "price_numeric": isinstance(event, dict) and isinstance(event.get("price"), (int, float)) and not isinstance(event.get("price"), bool),
        "simulated_false": isinstance(event, dict) and event.get("simulated") is False,
        "broker_order_not_created": isinstance(event, dict) and event.get("broker_order_created") is False,
        "live_order_not_created": isinstance(event, dict) and event.get("live_order_created") is False,
    }

    return {
        "status": "ok" if all(checks.values()) else "failed",
        "checks": checks,
        "certified": all(checks.values()),
        "safety_locks": SAFETY_LOCKS.copy(),
    }


def build_synthetic_validation_event(candidate_id: str, symbol: str) -> dict[str, Any]:
    return {
        "event_id": "synthetic_validation_event_001",
        "candidate_id": candidate_id,
        "symbol": symbol,
        "timestamp": "2024-01-02T00:00:00",
        "side": "hold",
        "quantity": 0,
        "price": 0.0,
        "reason": "shape_validation_only_no_trade_generated",
        "source": "33B_validation_stub",
        "simulated": False,
        "broker_order_created": False,
        "live_order_created": False,
    }
