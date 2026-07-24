#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()

SANDBOX_DIR = ROOT / "backend/app/stacks/strategy_candidate_sandbox"
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)

BRIDGE = SANDBOX_DIR / "hold_decision_to_hold_event_bridge.py"

OUT_DIR = ROOT / "runtime/strategy_candidate_sandbox"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT = OUT_DIR / "33G_hold_decision_to_hold_event_bridge_latest.json"
PHASE = "33G_HOLD_DECISION_TO_HOLD_EVENT_BRIDGE"

BRIDGE.write_text('''from __future__ import annotations

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
''', encoding="utf-8")

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "created_file": str(BRIDGE),
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    import py_compile
    py_compile.compile(str(BRIDGE), doraise=True)

    from backend.app.stacks.market_data.yfinance_historical_bars_adapter import get_historical_bars
    from backend.app.stacks.strategy_candidate_sandbox.hold_signal_generator_stub import generate_hold_signals
    from backend.app.stacks.strategy_candidate_sandbox.entry_exit_decision_engine_stub import decide_hold_only
    from backend.app.stacks.strategy_candidate_sandbox.hold_decision_to_hold_event_bridge import (
        bridge_hold_decisions_to_events,
        validate_hold_decision_bridge,
    )

    bars_response = get_historical_bars("AAPL", "2024-01-01", "2024-02-01", "1d")
    bars = bars_response.get("bars") if isinstance(bars_response, dict) else []

    signal_payload = generate_hold_signals("candidate_31e_stub_001", "AAPL", bars)
    signals = signal_payload.get("signals", [])

    decision_payload = decide_hold_only(signals)
    decisions = decision_payload.get("decisions", [])

    bridge_payload = bridge_hold_decisions_to_events(decisions)
    validation = validate_hold_decision_bridge(bridge_payload)

    result["input_summary"] = {
        "provider_status": bars_response.get("status") if isinstance(bars_response, dict) else None,
        "provider": bars_response.get("provider") if isinstance(bars_response, dict) else None,
        "bar_count": len(bars) if isinstance(bars, list) else 0,
        "signals": len(signals) if isinstance(signals, list) else 0,
        "decisions": len(decisions) if isinstance(decisions, list) else 0,
    }
    result["bridge_summary"] = {
        "status": bridge_payload.get("status"),
        "decisions_input": bridge_payload.get("decisions_input"),
        "hold_events_created": bridge_payload.get("hold_events_created"),
        "entry_events_created": bridge_payload.get("entry_events_created"),
        "exit_events_created": bridge_payload.get("exit_events_created"),
        "trades_simulated": bridge_payload.get("trades_simulated"),
        "broker_orders_created": bridge_payload.get("broker_orders_created"),
        "live_orders_created": bridge_payload.get("live_orders_created"),
        "simulation_enabled": bridge_payload.get("simulation_enabled"),
        "strategy_logic_enabled": bridge_payload.get("strategy_logic_enabled"),
    }
    result["first_event"] = bridge_payload.get("events", [None])[0] if bridge_payload.get("events") else None
    result["last_event"] = bridge_payload.get("events", [None])[-1] if bridge_payload.get("events") else None
    result["validation"] = validation

    result["checks"]["bridge_file_exists"] = BRIDGE.exists()
    result["checks"]["bridge_compiles"] = True
    result["checks"]["provider_status_ok"] = result["input_summary"]["provider_status"] == "ok"
    result["checks"]["provider_yfinance"] = result["input_summary"]["provider"] == "yfinance"
    result["checks"]["decisions_available"] = result["input_summary"]["decisions"] > 0
    result["checks"]["validation_certified"] = validation.get("certified") is True
    result["checks"]["hold_events_created_gt_zero"] = bridge_payload.get("hold_events_created", 0) > 0
    result["checks"]["hold_events_match_decisions"] = bridge_payload.get("hold_events_created") == len(decisions)
    result["checks"]["entry_events_zero"] = bridge_payload.get("entry_events_created") == 0
    result["checks"]["exit_events_zero"] = bridge_payload.get("exit_events_created") == 0
    result["checks"]["trades_simulated_zero"] = bridge_payload.get("trades_simulated") == 0
    result["checks"]["broker_orders_zero"] = bridge_payload.get("broker_orders_created") == 0
    result["checks"]["live_orders_zero"] = bridge_payload.get("live_orders_created") == 0
    result["checks"]["simulation_disabled"] = bridge_payload.get("simulation_enabled") is False
    result["checks"]["strategy_logic_disabled"] = bridge_payload.get("strategy_logic_enabled") is False
    result["checks"]["all_safety_locks_false"] = all(v is False for v in bridge_payload.get("safety_locks", {}).values())

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(json.dumps(result, indent=2))
print(f"\nWROTE: {OUT}")
