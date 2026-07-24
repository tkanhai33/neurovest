from __future__ import annotations

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
