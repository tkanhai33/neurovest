#!/usr/bin/env python3
import json
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "historical_bars_contract_v1.json"
TXT = SANDBOX / "historical_bars_contract_v1.txt"

SANDBOX.mkdir(parents=True, exist_ok=True)

contract = {
    "phase": "30C_HISTORICAL_BARS_CONTRACT",
    "generated_at": datetime.now(UTC).isoformat(),
    "schema_id": "historical_bars_contract_v1",
    "selected_provider": "yfinance",
    "bar_shape": {
        "timestamp": "ISO-8601|string",
        "open": "number",
        "high": "number",
        "low": "number",
        "close": "number",
        "volume": "number|null",
    },
    "provider_inputs": {
        "symbol": "string",
        "start_date": "YYYY-MM-DD",
        "end_date": "YYYY-MM-DD",
        "interval": "1d",
    },
    "provider_output": {
        "symbol": "string",
        "provider": "yfinance",
        "bars": "list[bar_shape]",
        "bar_count": "integer",
        "status": "ok|error",
        "error": "string|null",
    },
    "validation_rules": [
        "bars must be a list",
        "bar_count must equal len(bars)",
        "each bar must include timestamp/open/high/low/close/volume",
        "open/high/low/close must be numeric",
        "volume may be numeric or null",
        "no replay execution is allowed by this contract",
    ],
    "execution_flags": {
        "provider_wired": False,
        "market_data_enabled": False,
        "historical_replay_enabled": False,
        "simulation_enabled": False,
        "monte_carlo_enabled": False,
        "promotion_enabled": False,
        "live_execution_enabled": False,
        "broker_execution_enabled": False,
        "registry_write_enabled": False,
    },
    "notes": [
        "Historical bars shape contract only.",
        "yfinance selected but not wired.",
        "No bars loaded.",
        "No replay executed.",
    ],
}

OUT.write_text(json.dumps(contract, indent=2))

TXT.write_text("\n".join([
    "HISTORICAL BARS CONTRACT",
    f"Generated: {contract['generated_at']}",
    f"Schema: {contract['schema_id']}",
    "Selected Provider: yfinance",
    "Provider Wired: FALSE",
    "Market Data Enabled: FALSE",
    "Historical Replay Enabled: FALSE",
    "Simulation Enabled: FALSE",
    "Live Execution Enabled: FALSE",
    "Broker Execution Enabled: FALSE",
    "Registry Write Enabled: FALSE",
]))

print(json.dumps({
    "status": "ok",
    "contract_json": str(OUT),
    "contract_txt": str(TXT),
}, indent=2))
