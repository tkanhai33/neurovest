#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
OUT_DIR = ROOT / "runtime/strategy_candidate_sandbox"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT = OUT_DIR / "31E_first_single_candidate_replay_dry_run_latest.json"
PHASE = "31E_FIRST_SINGLE_CANDIDATE_REPLAY_DRY_RUN"

locks = {
    "live_execution_enabled": False,
    "broker_execution_enabled": False,
    "historical_replay_enabled": False,
    "simulation_enabled": False,
    "registry_write_enabled": False,
    "promotion_enabled": False,
    "learning_enabled": False,
}

candidate = {
    "candidate_id": "candidate_31e_stub_001",
    "name": "31E Iterator Dry Run Candidate",
    "symbol": "AAPL",
    "start": "2024-01-01",
    "end": "2024-02-01",
    "interval": "1d",
    "strategy_logic_enabled": False,
    "trade_simulation_enabled": False,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "candidate": candidate,
    "safety_locks": locks,
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    from backend.app.stacks.market_data.yfinance_historical_bars_adapter import get_historical_bars
    from backend.app.stacks.strategy_candidate_sandbox.historical_replay_bar_iterator import (
        summarize_bar_iteration,
    )
    from backend.app.stacks.strategy_candidate_sandbox.historical_replay_executor import (
        run_historical_replay,
    )

    executor_response = run_historical_replay(candidate)

    bars_response = get_historical_bars(
        candidate["symbol"],
        candidate["start"],
        candidate["end"],
        candidate["interval"],
    )

    bars = bars_response.get("bars") if isinstance(bars_response, dict) else []
    iterator_summary = summarize_bar_iteration(bars)

    dry_run = {
        "status": "dry_run_complete",
        "candidate_id": candidate["candidate_id"],
        "symbol": candidate["symbol"],
        "provider": bars_response.get("provider") if isinstance(bars_response, dict) else None,
        "provider_status": bars_response.get("status") if isinstance(bars_response, dict) else None,
        "bars_fetched": len(bars) if isinstance(bars, list) else 0,
        "bars_iterated": iterator_summary.get("bars_yielded"),
        "executor_status": executor_response.get("status") if isinstance(executor_response, dict) else None,
        "trades_simulated": 0,
        "metrics_generated": False,
        "scorecard_generated": False,
        "registry_written": False,
        "promotion_attempted": False,
        "learning_attempted": False,
    }

    result["executor_response"] = executor_response
    result["bars_response_summary"] = {
        "status": bars_response.get("status") if isinstance(bars_response, dict) else None,
        "provider": bars_response.get("provider") if isinstance(bars_response, dict) else None,
        "bar_count": len(bars) if isinstance(bars, list) else 0,
        "first_bar": bars[0] if isinstance(bars, list) and bars else None,
        "last_bar": bars[-1] if isinstance(bars, list) and bars else None,
    }
    result["iterator_summary"] = iterator_summary
    result["dry_run"] = dry_run

    result["checks"]["executor_remains_blocked_stub"] = dry_run["executor_status"] == "blocked_stub"
    result["checks"]["provider_status_ok"] = dry_run["provider_status"] == "ok"
    result["checks"]["provider_yfinance"] = dry_run["provider"] == "yfinance"
    result["checks"]["bars_fetched_gt_zero"] = dry_run["bars_fetched"] > 0
    result["checks"]["bars_iterated_equals_fetched"] = dry_run["bars_iterated"] == dry_run["bars_fetched"]
    result["checks"]["candidate_strategy_logic_disabled"] = candidate["strategy_logic_enabled"] is False
    result["checks"]["candidate_trade_simulation_disabled"] = candidate["trade_simulation_enabled"] is False
    result["checks"]["trades_simulated_zero"] = dry_run["trades_simulated"] == 0
    result["checks"]["metrics_not_generated"] = dry_run["metrics_generated"] is False
    result["checks"]["scorecard_not_generated"] = dry_run["scorecard_generated"] is False
    result["checks"]["registry_not_written"] = dry_run["registry_written"] is False
    result["checks"]["promotion_not_attempted"] = dry_run["promotion_attempted"] is False
    result["checks"]["learning_not_attempted"] = dry_run["learning_attempted"] is False
    result["checks"]["all_safety_locks_false"] = all(v is False for v in locks.values())

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(json.dumps(result, indent=2))
print(f"\nWROTE: {OUT}")
