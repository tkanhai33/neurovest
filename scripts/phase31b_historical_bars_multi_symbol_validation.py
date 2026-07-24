#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
OUT_DIR = ROOT / "runtime/strategy_candidate_sandbox"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT = OUT_DIR / "31B_historical_bars_multi_symbol_validation_latest.json"
PHASE = "31B_HISTORICAL_BARS_MULTI_SYMBOL_VALIDATION"

SYMBOLS = ["AAPL", "MSFT", "RY.TO", "SHOP.TO", "VFV.TO"]

locks = {
    "live_execution_enabled": False,
    "broker_execution_enabled": False,
    "historical_replay_enabled": False,
    "simulation_enabled": False,
    "registry_write_enabled": False,
    "promotion_enabled": False,
    "learning_enabled": False,
}

def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "target": {
        "symbols": SYMBOLS,
        "start": "2024-01-01",
        "end": "2024-02-01",
        "interval": "1d",
    },
    "safety_locks": locks,
    "symbol_results": [],
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    from backend.app.stacks.market_data.yfinance_historical_bars_adapter import get_historical_bars

    for symbol in SYMBOLS:
        response = get_historical_bars(symbol, "2024-01-01", "2024-02-01", "1d")
        bars = response.get("bars") if isinstance(response, dict) else None
        sample = bars[0] if isinstance(bars, list) and bars else {}

        checks = {
            "response_is_dict": isinstance(response, dict),
            "status_ok": isinstance(response, dict) and response.get("status") == "ok",
            "provider_yfinance": isinstance(response, dict) and response.get("provider") == "yfinance",
            "bars_is_list": isinstance(bars, list),
            "bar_count_gt_zero": isinstance(bars, list) and len(bars) > 0,
            "timestamp_exists": "timestamp" in sample,
            "ohlc_numeric": all(is_num(sample.get(k)) for k in ["open", "high", "low", "close"]),
            "volume_numeric_or_null": sample.get("volume") is None or is_num(sample.get("volume")),
        }

        result["symbol_results"].append({
            "symbol": symbol,
            "status": response.get("status") if isinstance(response, dict) else None,
            "provider": response.get("provider") if isinstance(response, dict) else None,
            "bar_count": len(bars) if isinstance(bars, list) else 0,
            "sample_bar": sample,
            "checks": checks,
            "certified": all(checks.values()),
            "error": response.get("error") if isinstance(response, dict) else "response_not_dict",
        })

    result["checks"]["all_symbols_certified"] = all(x["certified"] for x in result["symbol_results"])
    result["checks"]["all_safety_locks_false"] = all(v is False for v in locks.values())
    result["checks"]["symbol_count_expected"] = len(result["symbol_results"]) == len(SYMBOLS)
    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
print(f"\nWROTE: {OUT}")
