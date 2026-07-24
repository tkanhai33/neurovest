#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()

SANDBOX_DIR = ROOT / "backend/app/stacks/strategy_candidate_sandbox"
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)

DRY_RUN = SANDBOX_DIR / "trade_simulation_dry_run_stub.py"

OUT_DIR = ROOT / "runtime/strategy_candidate_sandbox"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT = OUT_DIR / "33C_trade_simulation_dry_run_stub_latest.json"
PHASE = "33C_TRADE_SIMULATION_DRY_RUN_STUB"

DRY_RUN.write_text('''from __future__ import annotations

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
''', encoding="utf-8")

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "created_file": str(DRY_RUN),
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    import py_compile
    py_compile.compile(str(DRY_RUN), doraise=True)

    from backend.app.stacks.market_data.yfinance_historical_bars_adapter import get_historical_bars
    from backend.app.stacks.strategy_candidate_sandbox.trade_simulation_dry_run_stub import (
        run_hold_only_trade_simulation_dry_run,
        validate_hold_only_dry_run,
    )

    bars_response = get_historical_bars("AAPL", "2024-01-01", "2024-02-01", "1d")
    bars = bars_response.get("bars") if isinstance(bars_response, dict) else []

    dry_run = run_hold_only_trade_simulation_dry_run(
        candidate_id="candidate_31e_stub_001",
        symbol="AAPL",
        bars=bars,
    )

    validation = validate_hold_only_dry_run(dry_run)

    result["bars_response_summary"] = {
        "status": bars_response.get("status") if isinstance(bars_response, dict) else None,
        "provider": bars_response.get("provider") if isinstance(bars_response, dict) else None,
        "bar_count": len(bars) if isinstance(bars, list) else 0,
    }
    result["dry_run_summary"] = {
        "status": dry_run.get("status"),
        "simulation_enabled": dry_run.get("simulation_enabled"),
        "bars_input": dry_run.get("bars_input"),
        "hold_events_created": dry_run.get("hold_events_created"),
        "validation_count": dry_run.get("validation_count"),
        "all_events_valid": dry_run.get("all_events_valid"),
        "trades_simulated": dry_run.get("trades_simulated"),
        "entries": dry_run.get("entries"),
        "exits": dry_run.get("exits"),
        "broker_orders_created": dry_run.get("broker_orders_created"),
        "live_orders_created": dry_run.get("live_orders_created"),
    }
    result["first_event"] = dry_run.get("trade_events", [None])[0] if dry_run.get("trade_events") else None
    result["last_event"] = dry_run.get("trade_events", [None])[-1] if dry_run.get("trade_events") else None
    result["validation"] = validation

    result["checks"]["dry_run_file_exists"] = DRY_RUN.exists()
    result["checks"]["dry_run_compiles"] = True
    result["checks"]["provider_status_ok"] = result["bars_response_summary"]["status"] == "ok"
    result["checks"]["provider_yfinance"] = result["bars_response_summary"]["provider"] == "yfinance"
    result["checks"]["bars_available"] = result["bars_response_summary"]["bar_count"] > 0
    result["checks"]["validation_certified"] = validation.get("certified") is True
    result["checks"]["simulation_enabled_false"] = dry_run.get("simulation_enabled") is False
    result["checks"]["hold_events_created_gt_zero"] = dry_run.get("hold_events_created", 0) > 0
    result["checks"]["hold_events_match_bars"] = dry_run.get("hold_events_created") == len(bars)
    result["checks"]["trades_simulated_zero"] = dry_run.get("trades_simulated") == 0
    result["checks"]["entries_zero"] = dry_run.get("entries") == 0
    result["checks"]["exits_zero"] = dry_run.get("exits") == 0
    result["checks"]["broker_orders_created_zero"] = dry_run.get("broker_orders_created") == 0
    result["checks"]["live_orders_created_zero"] = dry_run.get("live_orders_created") == 0
    result["checks"]["metrics_not_generated"] = dry_run.get("metrics_generated") is False
    result["checks"]["scorecard_not_generated"] = dry_run.get("scorecard_generated") is False
    result["checks"]["registry_not_written"] = dry_run.get("registry_written") is False
    result["checks"]["promotion_not_attempted"] = dry_run.get("promotion_attempted") is False
    result["checks"]["learning_not_attempted"] = dry_run.get("learning_attempted") is False
    result["checks"]["all_safety_locks_false"] = all(v is False for v in dry_run.get("safety_locks", {}).values())

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(json.dumps(result, indent=2))
print(f"\nWROTE: {OUT}")
