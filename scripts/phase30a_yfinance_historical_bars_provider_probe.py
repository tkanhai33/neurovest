#!/usr/bin/env python3
import json
import importlib
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "yfinance_historical_bars_provider_probe_latest.json"
TXT = SANDBOX / "yfinance_historical_bars_provider_probe_latest.txt"

SANDBOX.mkdir(parents=True, exist_ok=True)

probe = {
    "phase": "30A_YFINANCE_HISTORICAL_BARS_PROVIDER_PROBE",
    "generated_at": datetime.now(UTC).isoformat(),
    "provider_name": "yfinance",
    "provider_type": "historical_bars",
    "provider_imported": False,
    "provider_callable": False,
    "sample_symbols": [
        "AAPL",
        "RY.TO",
        "ABX.TO",
    ],
    "expected_output_shape": {
        "timestamp": "ISO-8601|string",
        "open": "number",
        "high": "number",
        "low": "number",
        "close": "number",
        "volume": "number|null",
    },
    "safe_for_replay_candidate": False,
    "historical_replay_enabled": False,
    "market_data_enabled": False,
    "simulation_enabled": False,
    "monte_carlo_enabled": False,
    "promotion_enabled": False,
    "live_execution_enabled": False,
    "broker_execution_enabled": False,
    "registry_write_enabled": False,
    "notes": [],
}

try:
    yf = importlib.import_module("yfinance")
    probe["provider_imported"] = True

    if hasattr(yf, "Ticker"):
        probe["provider_callable"] = True
        probe["safe_for_replay_candidate"] = True
        probe["notes"].append(
            "yfinance import successful and Ticker interface detected."
        )
    else:
        probe["notes"].append(
            "yfinance imported but Ticker interface missing."
        )

except Exception as exc:
    probe["notes"].append(f"yfinance import failed: {exc}")

OUT.write_text(json.dumps(probe, indent=2))

lines = [
    "YFINANCE HISTORICAL BARS PROVIDER PROBE",
    f"Generated: {probe['generated_at']}",
    f"Provider Imported: {probe['provider_imported']}",
    f"Provider Callable: {probe['provider_callable']}",
    f"Safe Replay Candidate: {probe['safe_for_replay_candidate']}",
    "",
    "Historical Replay Enabled: FALSE",
    "Market Data Enabled: FALSE",
    "Simulation Enabled: FALSE",
    "Monte Carlo Enabled: FALSE",
    "Promotion Enabled: FALSE",
    "Live Execution Enabled: FALSE",
    "Broker Execution Enabled: FALSE",
    "Registry Write Enabled: FALSE",
]

TXT.write_text("\n".join(lines))

print(json.dumps({
    "status": "ok",
    "provider_imported": probe["provider_imported"],
    "provider_callable": probe["provider_callable"],
    "safe_for_replay_candidate": probe["safe_for_replay_candidate"],
    "output_json": str(OUT),
    "output_txt": str(TXT),
}, indent=2))
