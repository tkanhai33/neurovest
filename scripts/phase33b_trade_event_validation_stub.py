#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()

SANDBOX_DIR = ROOT / "backend/app/stacks/strategy_candidate_sandbox"
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)

VALIDATOR = SANDBOX_DIR / "trade_event_validator.py"

OUT_DIR = ROOT / "runtime/strategy_candidate_sandbox"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT = OUT_DIR / "33B_trade_event_validation_stub_latest.json"
PHASE = "33B_TRADE_EVENT_VALIDATION_STUB"

VALIDATOR.write_text('''from __future__ import annotations

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

    from backend.app.stacks.strategy_candidate_sandbox.trade_event_validator import (
        build_synthetic_validation_event,
        validate_trade_event_shape,
    )

    event = build_synthetic_validation_event("candidate_31e_stub_001", "AAPL")
    validation = validate_trade_event_shape(event)

    result["sample_event"] = event
    result["validation"] = validation

    result["checks"]["validator_file_exists"] = VALIDATOR.exists()
    result["checks"]["validator_compiles"] = True
    result["checks"]["event_side_hold"] = event.get("side") == "hold"
    result["checks"]["event_quantity_zero"] = event.get("quantity") == 0
    result["checks"]["event_simulated_false"] = event.get("simulated") is False
    result["checks"]["broker_order_not_created"] = event.get("broker_order_created") is False
    result["checks"]["live_order_not_created"] = event.get("live_order_created") is False
    result["checks"]["validation_certified"] = validation.get("certified") is True
    result["checks"]["all_safety_locks_false"] = all(v is False for v in validation.get("safety_locks", {}).values())

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(json.dumps(result, indent=2))
print(f"\nWROTE: {OUT}")
