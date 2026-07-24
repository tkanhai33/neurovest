#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()

SANDBOX_DIR = ROOT / "backend/app/stacks/strategy_candidate_sandbox"
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)

CONTRACT = SANDBOX_DIR / "trade_simulation_contract.py"

OUT_DIR = ROOT / "runtime/strategy_candidate_sandbox"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT = OUT_DIR / "33A_trade_simulation_contract_stub_latest.json"
PHASE = "33A_TRADE_SIMULATION_CONTRACT_STUB"

CONTRACT.write_text('''from __future__ import annotations

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
''', encoding="utf-8")

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "created_file": str(CONTRACT),
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    import py_compile
    py_compile.compile(str(CONTRACT), doraise=True)

    from backend.app.stacks.strategy_candidate_sandbox.trade_simulation_contract import (
        build_empty_trade_simulation_contract,
        validate_trade_simulation_contract,
        TRADE_EVENT_CONTRACT_KEYS,
    )

    payload = build_empty_trade_simulation_contract(
        candidate_id="candidate_31e_stub_001",
        symbol="AAPL",
    )

    validation = validate_trade_simulation_contract(payload)

    result["trade_event_contract_keys"] = TRADE_EVENT_CONTRACT_KEYS
    result["sample_payload"] = payload
    result["validation"] = validation

    result["checks"]["contract_file_exists"] = CONTRACT.exists()
    result["checks"]["contract_compiles"] = True
    result["checks"]["payload_is_dict"] = isinstance(payload, dict)
    result["checks"]["validation_certified"] = validation.get("certified") is True
    result["checks"]["simulation_enabled_false"] = payload.get("simulation_enabled") is False
    result["checks"]["trade_events_empty"] = payload.get("trade_events") == []
    result["checks"]["trades_simulated_zero"] = payload.get("trades_simulated") == 0
    result["checks"]["broker_orders_created_zero"] = payload.get("broker_orders_created") == 0
    result["checks"]["live_orders_created_zero"] = payload.get("live_orders_created") == 0
    result["checks"]["metrics_not_generated"] = payload.get("metrics_generated") is False
    result["checks"]["scorecard_not_generated"] = payload.get("scorecard_generated") is False
    result["checks"]["registry_not_written"] = payload.get("registry_written") is False
    result["checks"]["promotion_not_attempted"] = payload.get("promotion_attempted") is False
    result["checks"]["learning_not_attempted"] = payload.get("learning_attempted") is False
    result["checks"]["all_safety_locks_false"] = all(v is False for v in payload.get("safety_locks", {}).values())

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(json.dumps(result, indent=2))
print(f"\nWROTE: {OUT}")
