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


def run_historical_replay(request: dict[str, Any]) -> dict[str, Any]:
    """
    Phase 31C stub only.

    This function intentionally does not execute replay logic.
    It only preserves the future executor contract while returning
    a locked response.
    """
    return {
        "status": "blocked_stub",
        "reason": "historical_replay_executor_is_stub_only",
        "request_received": isinstance(request, dict),
        "symbol": request.get("symbol") if isinstance(request, dict) else None,
        "candidate_id": request.get("candidate_id") if isinstance(request, dict) else None,
        "bars_iterated": 0,
        "trades_simulated": 0,
        "metrics_generated": False,
        "scorecard_generated": False,
        "registry_written": False,
        "promotion_attempted": False,
        "safety_locks": SAFETY_LOCKS.copy(),
    }
