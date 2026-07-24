from __future__ import annotations

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
