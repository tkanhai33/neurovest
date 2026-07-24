#!/usr/bin/env python3
import json
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"
OUT = SANDBOX / "yfinance_historical_bars_adapter_shape_validation_latest.json"
TXT = SANDBOX / "yfinance_historical_bars_adapter_shape_validation_latest.txt"

from backend.app.stacks.market_data.yfinance_historical_bars_adapter import get_historical_bars

sample = get_historical_bars("AAPL", "2024-01-01", "2024-02-01", "1d")

required_top = ["symbol", "provider", "bars", "bar_count", "status", "error", "execution_flags"]

shape_checks = {
    "top_level_is_dict": isinstance(sample, dict),
    "has_required_top_fields": all(key in sample for key in required_top),
    "provider_yfinance": sample.get("provider") == "yfinance",
    "bars_is_list": isinstance(sample.get("bars"), list),
    "bar_count_is_integer": isinstance(sample.get("bar_count"), int),
    "bar_count_matches_len": sample.get("bar_count") == len(sample.get("bars", [])),
    "status_not_wired": sample.get("status") == "not_wired",
    "execution_flags_present": isinstance(sample.get("execution_flags"), dict),
}

flags = sample.get("execution_flags", {})

lock_checks = {
    "provider_wired_false": flags.get("provider_wired") is False,
    "market_data_enabled_false": flags.get("market_data_enabled") is False,
    "historical_replay_enabled_false": flags.get("historical_replay_enabled") is False,
    "simulation_enabled_false": flags.get("simulation_enabled") is False,
    "live_execution_enabled_false": flags.get("live_execution_enabled") is False,
    "broker_execution_enabled_false": flags.get("broker_execution_enabled") is False,
    "registry_write_enabled_false": flags.get("registry_write_enabled") is False,
}

report = {
    "phase": "30E_YFINANCE_HISTORICAL_BARS_ADAPTER_SHAPE_VALIDATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "sample_symbol": "AAPL",
    "validation_status": "shape_validated_stub_only",
    "sample_response": sample,
    "shape_checks": shape_checks,
    "lock_checks": lock_checks,
    "certified_shape": all(shape_checks.values()) and all(lock_checks.values()),
    "notes": [
        "Shape validation only.",
        "Adapter remains stub-only.",
        "No bars loaded.",
        "No market data enabled.",
        "No historical replay executed.",
    ],
}

OUT.write_text(json.dumps(report, indent=2))

TXT.write_text("\n".join([
    "YFINANCE HISTORICAL BARS ADAPTER SHAPE VALIDATION",
    f"Generated: {report['generated_at']}",
    f"Validation Status: {report['validation_status']}",
    f"Certified Shape: {report['certified_shape']}",
    "Market Data Enabled: FALSE",
    "Historical Replay Enabled: FALSE",
    "Simulation Enabled: FALSE",
    "Live Execution Enabled: FALSE",
    "Broker Execution Enabled: FALSE",
    "Registry Write Enabled: FALSE",
]))

print(json.dumps({
    "status": "ok",
    "certified_shape": report["certified_shape"],
    "output_json": str(OUT),
    "output_txt": str(TXT),
}, indent=2))
