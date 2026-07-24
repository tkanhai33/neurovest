#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC
import math

ROOT = Path(".").resolve()

SANDBOX_DIR = ROOT / "backend/app/stacks/strategy_candidate_sandbox"
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)

GENERATOR = SANDBOX_DIR / "replay_metrics_generator.py"

OUT_DIR = ROOT / "runtime/strategy_candidate_sandbox"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT = OUT_DIR / "32A_real_metrics_generation_latest.json"
PHASE = "32A_REAL_METRICS_GENERATION"

GENERATOR.write_text('''from __future__ import annotations

from typing import Any
import math


SAFETY_LOCKS = {
    "live_execution_enabled": False,
    "broker_execution_enabled": False,
    "historical_replay_enabled": False,
    "simulation_enabled": False,
    "registry_write_enabled": False,
    "promotion_enabled": False,
    "learning_enabled": False,
}


def _num(value: Any) -> float | None:
    try:
        out = float(value)
        if math.isnan(out):
            return None
        return out
    except Exception:
        return None


def generate_bar_only_metrics(
    candidate_id: str,
    symbol: str,
    provider: str,
    bars: list[dict[str, Any]],
) -> dict[str, Any]:
    closes = []

    if isinstance(bars, list):
        for bar in bars:
            close = _num(bar.get("close")) if isinstance(bar, dict) else None
            if close is not None and close > 0:
                closes.append(close)

    returns = []
    for i in range(1, len(closes)):
        prev = closes[i - 1]
        cur = closes[i]
        if prev > 0:
            returns.append((cur - prev) / prev)

    total_return_pct = None
    if len(closes) >= 2 and closes[0] > 0:
        total_return_pct = ((closes[-1] - closes[0]) / closes[0]) * 100

    max_drawdown_pct = None
    if closes:
        peak = closes[0]
        max_dd = 0.0
        for close in closes:
            if close > peak:
                peak = close
            if peak > 0:
                dd = (close - peak) / peak
                if dd < max_dd:
                    max_dd = dd
        max_drawdown_pct = max_dd * 100

    avg_bar_return_pct = None
    if returns:
        avg_bar_return_pct = (sum(returns) / len(returns)) * 100

    volatility_pct = None
    if len(returns) >= 2:
        mean = sum(returns) / len(returns)
        variance = sum((r - mean) ** 2 for r in returns) / (len(returns) - 1)
        volatility_pct = math.sqrt(variance) * 100

    return {
        "candidate_id": candidate_id,
        "symbol": symbol,
        "provider": provider,
        "bars_input": len(bars) if isinstance(bars, list) else 0,
        "bars_used": len(closes),
        "trades_simulated": 0,
        "entries": 0,
        "exits": 0,
        "wins": 0,
        "losses": 0,
        "win_rate": None,
        "total_return_pct": total_return_pct,
        "max_drawdown_pct": max_drawdown_pct,
        "avg_bar_return_pct": avg_bar_return_pct,
        "volatility_pct": volatility_pct,
        "avg_trade_return_pct": None,
        "profit_factor": None,
        "sharpe_like": None,
        "metrics_generated": True,
        "metrics_mode": "bar_only_no_trades",
        "scorecard_generated": False,
        "registry_written": False,
        "promotion_attempted": False,
        "learning_attempted": False,
        "safety_locks": SAFETY_LOCKS.copy(),
    }


def validate_bar_only_metrics(payload: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "payload_is_dict": isinstance(payload, dict),
        "metrics_generated_true": payload.get("metrics_generated") is True,
        "metrics_mode_bar_only": payload.get("metrics_mode") == "bar_only_no_trades",
        "bars_used_gt_zero": payload.get("bars_used", 0) > 0,
        "trades_simulated_zero": payload.get("trades_simulated") == 0,
        "entries_zero": payload.get("entries") == 0,
        "exits_zero": payload.get("exits") == 0,
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
    from backend.app.stacks.strategy_candidate_sandbox.replay_metrics_generator import (
        generate_bar_only_metrics,
        validate_bar_only_metrics,
    )

    bars_response = get_historical_bars("AAPL", "2024-01-01", "2024-02-01", "1d")
    bars = bars_response.get("bars") if isinstance(bars_response, dict) else []

    metrics = generate_bar_only_metrics(
        candidate_id="candidate_31e_stub_001",
        symbol="AAPL",
        provider="yfinance",
        bars=bars,
    )

    validation = validate_bar_only_metrics(metrics)

    result["bars_response_summary"] = {
        "status": bars_response.get("status") if isinstance(bars_response, dict) else None,
        "provider": bars_response.get("provider") if isinstance(bars_response, dict) else None,
        "bar_count": len(bars) if isinstance(bars, list) else 0,
    }

    result["metrics"] = metrics
    result["validation"] = validation

    result["checks"]["generator_file_exists"] = GENERATOR.exists()
    result["checks"]["generator_compiles"] = True
    result["checks"]["provider_status_ok"] = result["bars_response_summary"]["status"] == "ok"
    result["checks"]["provider_yfinance"] = result["bars_response_summary"]["provider"] == "yfinance"
    result["checks"]["bars_available"] = result["bars_response_summary"]["bar_count"] > 0
    result["checks"]["validation_certified"] = validation.get("certified") is True
    result["checks"]["metrics_generated_true"] = metrics.get("metrics_generated") is True
    result["checks"]["metrics_mode_bar_only"] = metrics.get("metrics_mode") == "bar_only_no_trades"
    result["checks"]["total_return_calculated"] = isinstance(metrics.get("total_return_pct"), (int, float))
    result["checks"]["max_drawdown_calculated"] = isinstance(metrics.get("max_drawdown_pct"), (int, float))
    result["checks"]["trades_simulated_zero"] = metrics.get("trades_simulated") == 0
    result["checks"]["scorecard_not_generated"] = metrics.get("scorecard_generated") is False
    result["checks"]["registry_not_written"] = metrics.get("registry_written") is False
    result["checks"]["promotion_not_attempted"] = metrics.get("promotion_attempted") is False
    result["checks"]["learning_not_attempted"] = metrics.get("learning_attempted") is False
    result["checks"]["all_safety_locks_false"] = all(v is False for v in metrics.get("safety_locks", {}).values())

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(json.dumps(result, indent=2))
print(f"\nWROTE: {OUT}")
