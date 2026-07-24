#!/usr/bin/env python3
import json
import math
from datetime import datetime, UTC
from pathlib import Path

from backend.app.stacks.market_data.yfinance_historical_bars_adapter import get_historical_bars

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"
OUT = SANDBOX / "historical_bars_fetch_validation_latest.json"
TXT = SANDBOX / "historical_bars_fetch_validation_latest.txt"

SANDBOX.mkdir(parents=True, exist_ok=True)

sample = get_historical_bars("AAPL", "2024-01-01", "2024-02-01", "1d")
bars = sample.get("bars", [])

def is_number(value):
    return isinstance(value, (int, float)) and not math.isnan(float(value))

bar_checks = []

for bar in bars:
    bar_checks.append({
        "timestamp_exists": bool(bar.get("timestamp")),
        "open_numeric": is_number(bar.get("open")),
        "high_numeric": is_number(bar.get("high")),
        "low_numeric": is_number(bar.get("low")),
        "close_numeric": is_number(bar.get("close")),
        "volume_valid": bar.get("volume") is None or is_number(bar.get("volume")),
    })

all_bars_valid = all(all(item.values()) for item in bar_checks) if bar_checks else False

flags = sample.get("execution_flags", {})

checks = {
    "provider_yfinance": sample.get("provider") == "yfinance",
    "status_ok": sample.get("status") == "ok",
    "bars_is_list": isinstance(bars, list),
    "bar_count_positive": isinstance(sample.get("bar_count"), int) and sample.get("bar_count") > 0,
    "bar_count_matches_len": sample.get("bar_count") == len(bars),
    "all_bars_valid": all_bars_valid,
    "provider_wired_true": flags.get("provider_wired") is True,
    "market_data_enabled_true": flags.get("market_data_enabled") is True,
    "historical_replay_disabled": flags.get("historical_replay_enabled") is False,
    "simulation_disabled": flags.get("simulation_enabled") is False,
    "live_execution_disabled": flags.get("live_execution_enabled") is False,
    "broker_execution_disabled": flags.get("broker_execution_enabled") is False,
    "registry_write_disabled": flags.get("registry_write_enabled") is False,
}

report = {
    "phase": "31A_HISTORICAL_BARS_FETCH_VALIDATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "symbol": "AAPL",
    "start_date": "2024-01-01",
    "end_date": "2024-02-01",
    "interval": "1d",
    "validated": all(checks.values()),
    "checks": checks,
    "bar_count": sample.get("bar_count"),
    "sample_first_bar": bars[0] if bars else None,
    "sample_last_bar": bars[-1] if bars else None,
    "source_response_status": sample.get("status"),
    "source_response_error": sample.get("error"),
    "execution_flags": flags,
}

OUT.write_text(json.dumps(report, indent=2))

TXT.write_text("\n".join([
    "HISTORICAL BARS FETCH VALIDATION",
    f"Generated: {report['generated_at']}",
    "Provider: yfinance",
    "Symbol: AAPL",
    f"Validated: {report['validated']}",
    f"Bar Count: {report['bar_count']}",
    "Historical Replay Enabled: FALSE",
    "Simulation Enabled: FALSE",
    "Live Execution Enabled: FALSE",
    "Broker Execution Enabled: FALSE",
    "Registry Write Enabled: FALSE",
]))

print(json.dumps({
    "status": "ok",
    "validated": report["validated"],
    "bar_count": report["bar_count"],
    "output_json": str(OUT),
    "output_txt": str(TXT),
}, indent=2))

if not report["validated"]:
    raise SystemExit(1)
