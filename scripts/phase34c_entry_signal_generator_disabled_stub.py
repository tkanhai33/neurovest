#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX_DIR = ROOT / "backend/app/stacks/strategy_candidate_sandbox"
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)

GENERATOR = SANDBOX_DIR / "entry_signal_generator_disabled_stub.py"
OUT_DIR = ROOT / "runtime/strategy_candidate_sandbox"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT = OUT_DIR / "34C_entry_signal_generator_disabled_stub_latest.json"

PHASE = "34C_ENTRY_SIGNAL_GENERATOR_DISABLED_STUB"

GENERATOR.write_text('''from __future__ import annotations

from typing import Any

from backend.app.stacks.strategy_candidate_sandbox.trade_simulation_contract import SAFETY_LOCKS
from backend.app.stacks.strategy_candidate_sandbox.entry_signal_rule_validator import validate_disabled_entry_rule


def generate_entry_signals_disabled(
    candidate_id: str,
    symbol: str,
    bars: list[dict[str, Any]],
    rule: dict[str, Any],
) -> dict[str, Any]:
    rule_validation = validate_disabled_entry_rule(rule)

    return {
        "status": "entry_signal_generator_disabled_stub",
        "candidate_id": candidate_id,
        "symbol": symbol,
        "bars_input": len(bars) if isinstance(bars, list) else 0,
        "rule_validated": rule_validation.get("certified") is True,
        "rule_enabled": rule.get("enabled") if isinstance(rule, dict) else None,
        "entry_signal_generation_enabled": rule.get("entry_signal_generation_enabled") if isinstance(rule, dict) else None,
        "strategy_logic_enabled": rule.get("strategy_logic_enabled") if isinstance(rule, dict) else None,
        "entry_signals_created": 0,
        "signals": [],
        "exit_signals_created": 0,
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


def validate_entry_signal_generator_disabled(payload: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "payload_is_dict": isinstance(payload, dict),
        "status_ok": payload.get("status") == "entry_signal_generator_disabled_stub",
        "bars_input_gt_zero": payload.get("bars_input", 0) > 0,
        "rule_validated": payload.get("rule_validated") is True,
        "rule_enabled_false": payload.get("rule_enabled") is False,
        "entry_generation_disabled": payload.get("entry_signal_generation_enabled") is False,
        "strategy_logic_disabled": payload.get("strategy_logic_enabled") is False,
        "entry_signals_zero": payload.get("entry_signals_created") == 0,
        "signals_empty": payload.get("signals") == [],
        "exit_signals_zero": payload.get("exit_signals_created") == 0,
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
    from backend.app.stacks.strategy_candidate_sandbox.entry_signal_rule_contract import build_disabled_entry_rule_contract
    from backend.app.stacks.strategy_candidate_sandbox.entry_signal_generator_disabled_stub import (
        generate_entry_signals_disabled,
        validate_entry_signal_generator_disabled,
    )

    bars_response = get_historical_bars("AAPL", "2024-01-01", "2024-02-01", "1d")
    bars = bars_response.get("bars") if isinstance(bars_response, dict) else []

    rule = build_disabled_entry_rule_contract("candidate_31e_stub_001", "AAPL")
    generated = generate_entry_signals_disabled("candidate_31e_stub_001", "AAPL", bars, rule)
    validation = validate_entry_signal_generator_disabled(generated)

    result["bars_response_summary"] = {
        "status": bars_response.get("status") if isinstance(bars_response, dict) else None,
        "provider": bars_response.get("provider") if isinstance(bars_response, dict) else None,
        "bar_count": len(bars) if isinstance(bars, list) else 0,
    }
    result["generation_summary"] = {
        "status": generated.get("status"),
        "bars_input": generated.get("bars_input"),
        "rule_validated": generated.get("rule_validated"),
        "rule_enabled": generated.get("rule_enabled"),
        "entry_signal_generation_enabled": generated.get("entry_signal_generation_enabled"),
        "strategy_logic_enabled": generated.get("strategy_logic_enabled"),
        "entry_signals_created": generated.get("entry_signals_created"),
        "trade_events_created": generated.get("trade_events_created"),
    }
    result["validation"] = validation

    result["checks"]["generator_file_exists"] = GENERATOR.exists()
    result["checks"]["generator_compiles"] = True
    result["checks"]["provider_status_ok"] = result["bars_response_summary"]["status"] == "ok"
    result["checks"]["provider_yfinance"] = result["bars_response_summary"]["provider"] == "yfinance"
    result["checks"]["bars_available"] = result["bars_response_summary"]["bar_count"] > 0
    result["checks"]["validation_certified"] = validation.get("certified") is True
    result["checks"]["rule_validated"] = generated.get("rule_validated") is True
    result["checks"]["entry_signals_zero"] = generated.get("entry_signals_created") == 0
    result["checks"]["signals_empty"] = generated.get("signals") == []
    result["checks"]["strategy_logic_disabled"] = generated.get("strategy_logic_enabled") is False
    result["checks"]["entry_generation_disabled"] = generated.get("entry_signal_generation_enabled") is False
    result["checks"]["trade_events_zero"] = generated.get("trade_events_created") == 0
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
