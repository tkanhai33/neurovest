#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()

REPLAY_DIR = ROOT / "backend/app/stacks/strategy_candidate_sandbox"
REPLAY_DIR.mkdir(parents=True, exist_ok=True)

EXECUTOR = REPLAY_DIR / "historical_replay_executor.py"

OUT_DIR = ROOT / "runtime/strategy_candidate_sandbox"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT = OUT_DIR / "31C_historical_replay_executor_stub_latest.json"

PHASE = "31C_HISTORICAL_REPLAY_EXECUTOR_STUB"

EXECUTOR.write_text('''from __future__ import annotations

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
''', encoding="utf-8")

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "created_file": str(EXECUTOR),
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    import py_compile
    py_compile.compile(str(EXECUTOR), doraise=True)

    from backend.app.stacks.strategy_candidate_sandbox.historical_replay_executor import (
        run_historical_replay,
        SAFETY_LOCKS,
    )

    sample_request = {
        "candidate_id": "candidate_stub_001",
        "symbol": "AAPL",
        "start": "2024-01-01",
        "end": "2024-02-01",
        "interval": "1d",
    }

    response = run_historical_replay(sample_request)

    result["sample_response"] = response

    result["checks"]["executor_file_exists"] = EXECUTOR.exists()
    result["checks"]["executor_compiles"] = True
    result["checks"]["response_is_dict"] = isinstance(response, dict)
    result["checks"]["status_blocked_stub"] = response.get("status") == "blocked_stub"
    result["checks"]["bars_iterated_zero"] = response.get("bars_iterated") == 0
    result["checks"]["trades_simulated_zero"] = response.get("trades_simulated") == 0
    result["checks"]["metrics_not_generated"] = response.get("metrics_generated") is False
    result["checks"]["scorecard_not_generated"] = response.get("scorecard_generated") is False
    result["checks"]["registry_not_written"] = response.get("registry_written") is False
    result["checks"]["promotion_not_attempted"] = response.get("promotion_attempted") is False
    result["checks"]["all_safety_locks_false"] = all(v is False for v in SAFETY_LOCKS.values())

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(json.dumps(result, indent=2))
print(f"\nWROTE: {OUT}")
