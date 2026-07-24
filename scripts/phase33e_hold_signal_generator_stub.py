#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()

SANDBOX_DIR = ROOT / "backend/app/stacks/strategy_candidate_sandbox"
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)

GENERATOR = SANDBOX_DIR / "hold_signal_generator_stub.py"

OUT_DIR = ROOT / "runtime/strategy_candidate_sandbox"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT = OUT_DIR / "33E_hold_signal_generator_stub_latest.json"
PHASE = "33E_HOLD_SIGNAL_GENERATOR_STUB"

GENERATOR.write_text('''from __future__ import annotations

from typing import Any

from backend.app.stacks.strategy_candidate_sandbox.entry_exit_signal_contract import validate_signal_contract
from backend.app.stacks.strategy_candidate_sandbox.trade_simulation_contract import SAFETY_LOCKS


def build_hold_signal(candidate_id: str, symbol: str, bar: dict[str, Any], index: int) -> dict[str, Any]:
    return {
        "signal_id": f"hold_signal_{index:06d}",
        "candidate_id": candidate_id,
        "symbol": symbol,
        "timestamp": bar.get("timestamp"),
        "signal_type": "hold",
        "confidence": 0.0,
        "price": float(bar.get("close")),
        "reason": "33E_hold_only_signal_no_entry_exit_logic",
        "source": "33E_hold_signal_generator_stub",
        "strategy_logic_enabled": False,
        "simulation_enabled": False,
        "trade_event_created": False,
    }


def generate_hold_signals(candidate_id: str, symbol: str, bars: list[dict[str, Any]]) -> dict[str, Any]:
    signals = []
    validations = []

    if isinstance(bars, list):
        for index, bar in enumerate(bars):
            if not isinstance(bar, dict):
                continue
            if "timestamp" not in bar or "close" not in bar:
                continue

            signal = build_hold_signal(candidate_id, symbol, bar, index)
            validation = validate_signal_contract(signal)

            if validation.get("certified") is True:
                signals.append(signal)

            validations.append(validation)

    return {
        "status": "hold_signals_generated_stub",
        "candidate_id": candidate_id,
        "symbol": symbol,
        "bars_input": len(bars) if isinstance(bars, list) else 0,
        "hold_signals_created": len(signals),
        "signals": signals,
        "validation_count": len(validations),
        "all_signals_valid": all(v.get("certified") is True for v in validations) if validations else False,
        "entry_signals_created": 0,
        "exit_signals_created": 0,
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


def validate_hold_signal_generation(payload: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "payload_is_dict": isinstance(payload, dict),
        "status_ok": payload.get("status") == "hold_signals_generated_stub",
        "hold_signals_created_gt_zero": payload.get("hold_signals_created", 0) > 0,
        "hold_signals_match_bars": payload.get("hold_signals_created") == payload.get("bars_input"),
        "all_signals_valid": payload.get("all_signals_valid") is True,
        "entry_signals_zero": payload.get("entry_signals_created") == 0,
        "exit_signals_zero": payload.get("exit_signals_created") == 0,
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
    "created_file": str(GENERATOR),
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    import py_compile
    py_compile.compile(str(GENERATOR), doraise=True)

    from backend.app.stacks.market_data.yfinance_historical_bars_adapter import get_historical_bars
    from backend.app.stacks.strategy_candidate_sandbox.hold_signal_generator_stub import (
        generate_hold_signals,
        validate_hold_signal_generation,
    )

    bars_response = get_historical_bars("AAPL", "2024-01-01", "2024-02-01", "1d")
    bars = bars_response.get("bars") if isinstance(bars_response, dict) else []

    generated = generate_hold_signals("candidate_31e_stub_001", "AAPL", bars)
    validation = validate_hold_signal_generation(generated)

    result["bars_response_summary"] = {
        "status": bars_response.get("status") if isinstance(bars_response, dict) else None,
        "provider": bars_response.get("provider") if isinstance(bars_response, dict) else None,
        "bar_count": len(bars) if isinstance(bars, list) else 0,
    }
    result["generation_summary"] = {
        "status": generated.get("status"),
        "bars_input": generated.get("bars_input"),
        "hold_signals_created": generated.get("hold_signals_created"),
        "entry_signals_created": generated.get("entry_signals_created"),
        "exit_signals_created": generated.get("exit_signals_created"),
        "trade_events_created": generated.get("trade_events_created"),
        "strategy_logic_enabled": generated.get("strategy_logic_enabled"),
        "simulation_enabled": generated.get("simulation_enabled"),
        "all_signals_valid": generated.get("all_signals_valid"),
    }
    result["first_signal"] = generated.get("signals", [None])[0] if generated.get("signals") else None
    result["last_signal"] = generated.get("signals", [None])[-1] if generated.get("signals") else None
    result["validation"] = validation

    result["checks"]["generator_file_exists"] = GENERATOR.exists()
    result["checks"]["generator_compiles"] = True
    result["checks"]["provider_status_ok"] = result["bars_response_summary"]["status"] == "ok"
    result["checks"]["provider_yfinance"] = result["bars_response_summary"]["provider"] == "yfinance"
    result["checks"]["bars_available"] = result["bars_response_summary"]["bar_count"] > 0
    result["checks"]["validation_certified"] = validation.get("certified") is True
    result["checks"]["hold_signals_created_gt_zero"] = generated.get("hold_signals_created", 0) > 0
    result["checks"]["hold_signals_match_bars"] = generated.get("hold_signals_created") == len(bars)
    result["checks"]["entry_signals_zero"] = generated.get("entry_signals_created") == 0
    result["checks"]["exit_signals_zero"] = generated.get("exit_signals_created") == 0
    result["checks"]["trade_events_zero"] = generated.get("trade_events_created") == 0
    result["checks"]["strategy_logic_disabled"] = generated.get("strategy_logic_enabled") is False
    result["checks"]["simulation_disabled"] = generated.get("simulation_enabled") is False
    result["checks"]["all_safety_locks_false"] = all(v is False for v in generated.get("safety_locks", {}).values())

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(json.dumps(result, indent=2))
print(f"\nWROTE: {OUT}")
