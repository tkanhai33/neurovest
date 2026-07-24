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


REPLAY_METRICS_CONTRACT_KEYS = [
    "candidate_id",
    "symbol",
    "provider",
    "bars_input",
    "bars_iterated",
    "trades_simulated",
    "entries",
    "exits",
    "wins",
    "losses",
    "win_rate",
    "total_return_pct",
    "max_drawdown_pct",
    "avg_trade_return_pct",
    "profit_factor",
    "sharpe_like",
    "metrics_generated",
    "scorecard_generated",
    "registry_written",
    "promotion_attempted",
    "learning_attempted",
]


def build_empty_replay_metrics_contract(
    candidate_id: str,
    symbol: str,
    provider: str,
    bars_input: int,
    bars_iterated: int,
) -> dict[str, Any]:
    return {
        "candidate_id": candidate_id,
        "symbol": symbol,
        "provider": provider,
        "bars_input": bars_input,
        "bars_iterated": bars_iterated,
        "trades_simulated": 0,
        "entries": 0,
        "exits": 0,
        "wins": 0,
        "losses": 0,
        "win_rate": None,
        "total_return_pct": None,
        "max_drawdown_pct": None,
        "avg_trade_return_pct": None,
        "profit_factor": None,
        "sharpe_like": None,
        "metrics_generated": False,
        "scorecard_generated": False,
        "registry_written": False,
        "promotion_attempted": False,
        "learning_attempted": False,
        "safety_locks": SAFETY_LOCKS.copy(),
    }


def validate_replay_metrics_contract(payload: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "payload_is_dict": isinstance(payload, dict),
        "all_contract_keys_present": all(k in payload for k in REPLAY_METRICS_CONTRACT_KEYS),
        "trades_simulated_zero": payload.get("trades_simulated") == 0,
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
