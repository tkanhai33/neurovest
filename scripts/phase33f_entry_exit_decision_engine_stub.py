#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()

SANDBOX_DIR = ROOT / "backend/app/stacks/strategy_candidate_sandbox"
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)

ENGINE = SANDBOX_DIR / "entry_exit_decision_engine_stub.py"

OUT_DIR = ROOT / "runtime/strategy_candidate_sandbox"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT = OUT_DIR / "33F_entry_exit_decision_engine_stub_latest.json"
PHASE = "33F_ENTRY_EXIT_DECISION_ENGINE_STUB"

ENGINE.write_text('''from __future__ import annotations

from typing import Any

from backend.app.stacks.strategy_candidate_sandbox.trade_simulation_contract import SAFETY_LOCKS


def decide_hold_only(signals: list[dict[str, Any]]) -> dict[str, Any]:
    decisions = []

    if isinstance(signals, list):
        for index, signal in enumerate(signals):
            if not isinstance(signal, dict):
                continue

            decisions.append({
                "decision_id": f"hold_decision_{index:06d}",
                "signal_id": signal.get("signal_id"),
                "candidate_id": signal.get("candidate_id"),
                "symbol": signal.get("symbol"),
                "timestamp": signal.get("timestamp"),
                "decision": "hold",
                "confidence": 0.0,
                "reason": "33F_decision_engine_stub_hold_only_no_entry_exit_logic",
                "entry_decision_created": False,
                "exit_decision_created": False,
                "trade_event_created": False,
                "strategy_logic_enabled": False,
                "simulation_enabled": False,
            })

    return {
        "status": "hold_only_decisions_generated_stub",
        "signals_input": len(signals) if isinstance(signals, list) else 0,
        "decisions_created": len(decisions),
        "decisions": decisions,
        "entry_decisions_created": 0,
        "exit_decisions_created": 0,
        "trade_events_created": 0,
        "strategy_logic_enabled": False,
        "simulation_enabled": False,
        "trades_simulated": 0,
        "broker_orders_created": 0,
        "live_orders_created": 0,
        "metrics_generated": False,
        "scorecard_generated": False,
        "registry_written": False,
        "promotion_attempted": False,
        "learning_attempted": False,
        "safety_locks": SAFETY_LOCKS.copy(),
    }


def validate_decision_engine_stub(payload: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "payload_is_dict": isinstance(payload, dict),
        "status_ok": payload.get("status") == "hold_only_decisions_generated_stub",
        "decisions_created_gt_zero": payload.get("decisions_created", 0) > 0,
        "decisions_match_signals": payload.get("decisions_created") == payload.get("signals_input"),
        "entry_decisions_zero": payload.get("entry_decisions_created") == 0,
        "exit_decisions_zero": payload.get("exit_decisions_created") == 0,
        "trade_events_zero": payload.get("trade_events_created") == 0,
        "strategy_logic_disabled": payload.get("strategy_logic_enabled") is False,
        "simulation_disabled": payload.get("simulation_enabled") is False,
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
''', encoding="utf-8")

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "created_file": str(ENGINE),
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    import py_compile
    py_compile.compile(str(ENGINE), doraise=True)

    from backend.app.stacks.market_data.yfinance_historical_bars_adapter import get_historical_bars
    from backend.app.stacks.strategy_candidate_sandbox.hold_signal_generator_stub import generate_hold_signals
    from backend.app.stacks.strategy_candidate_sandbox.entry_exit_decision_engine_stub import (
        decide_hold_only,
        validate_decision_engine_stub,
    )

    bars_response = get_historical_bars("AAPL", "2024-01-01", "2024-02-01", "1d")
    bars = bars_response.get("bars") if isinstance(bars_response, dict) else []

    generated = generate_hold_signals("candidate_31e_stub_001", "AAPL", bars)
    signals = generated.get("signals", [])

    decisions = decide_hold_only(signals)
    validation = validate_decision_engine_stub(decisions)

    result["input_summary"] = {
        "provider_status": bars_response.get("status") if isinstance(bars_response, dict) else None,
        "provider": bars_response.get("provider") if isinstance(bars_response, dict) else None,
        "bar_count": len(bars) if isinstance(bars, list) else 0,
        "signals_input": len(signals) if isinstance(signals, list) else 0,
    }
    result["decision_summary"] = {
        "status": decisions.get("status"),
        "signals_input": decisions.get("signals_input"),
        "decisions_created": decisions.get("decisions_created"),
        "entry_decisions_created": decisions.get("entry_decisions_created"),
        "exit_decisions_created": decisions.get("exit_decisions_created"),
        "trade_events_created": decisions.get("trade_events_created"),
        "strategy_logic_enabled": decisions.get("strategy_logic_enabled"),
        "simulation_enabled": decisions.get("simulation_enabled"),
    }
    result["first_decision"] = decisions.get("decisions", [None])[0] if decisions.get("decisions") else None
    result["last_decision"] = decisions.get("decisions", [None])[-1] if decisions.get("decisions") else None
    result["validation"] = validation

    result["checks"]["engine_file_exists"] = ENGINE.exists()
    result["checks"]["engine_compiles"] = True
    result["checks"]["provider_status_ok"] = result["input_summary"]["provider_status"] == "ok"
    result["checks"]["provider_yfinance"] = result["input_summary"]["provider"] == "yfinance"
    result["checks"]["signals_available"] = result["input_summary"]["signals_input"] > 0
    result["checks"]["validation_certified"] = validation.get("certified") is True
    result["checks"]["decisions_created_gt_zero"] = decisions.get("decisions_created", 0) > 0
    result["checks"]["decisions_match_signals"] = decisions.get("decisions_created") == len(signals)
    result["checks"]["entry_decisions_zero"] = decisions.get("entry_decisions_created") == 0
    result["checks"]["exit_decisions_zero"] = decisions.get("exit_decisions_created") == 0
    result["checks"]["trade_events_zero"] = decisions.get("trade_events_created") == 0
    result["checks"]["strategy_logic_disabled"] = decisions.get("strategy_logic_enabled") is False
    result["checks"]["simulation_disabled"] = decisions.get("simulation_enabled") is False
    result["checks"]["all_safety_locks_false"] = all(v is False for v in decisions.get("safety_locks", {}).values())

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(json.dumps(result, indent=2))
print(f"\nWROTE: {OUT}")
