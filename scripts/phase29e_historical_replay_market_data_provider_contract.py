#!/usr/bin/env python3
import json
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"
OUT = SANDBOX / "historical_replay_market_data_provider_contract_v1.json"
TXT = SANDBOX / "historical_replay_market_data_provider_contract_v1.txt"

SANDBOX.mkdir(parents=True, exist_ok=True)

contract = {
    "phase": "29E_HISTORICAL_REPLAY_MARKET_DATA_PROVIDER_CONTRACT",
    "generated_at": datetime.now(UTC).isoformat(),
    "schema_id": "historical_replay_market_data_provider_contract_v1",
    "provider_contract": {
        "provider_name": "not_wired",
        "provider_type": "historical_bars",
        "required_function": "get_historical_bars",
        "required_inputs": {
            "symbol": "string",
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD",
            "interval": "1d|1h|15m|5m",
        },
        "required_output_shape": {
            "symbol": "string",
            "provider": "string",
            "bars": [
                {
                    "timestamp": "ISO-8601|string",
                    "open": "number",
                    "high": "number",
                    "low": "number",
                    "close": "number",
                    "volume": "number|null",
                }
            ],
            "bar_count": "integer",
            "status": "ok|error",
            "error": "string|null",
        },
    },
    "certification_requirements": [
        "provider import must compile",
        "provider must return deterministic shape",
        "provider must not place orders",
        "provider must not mutate strategy registry",
        "provider must not enable live execution",
        "provider must not enable broker execution",
    ],
    "execution_flags": {
        "provider_wired": False,
        "market_data_enabled": False,
        "historical_replay_enabled": False,
        "simulation_enabled": False,
        "live_execution_enabled": False,
        "broker_execution_enabled": False,
        "registry_write_enabled": False,
    },
    "notes": [
        "Market data provider contract only.",
        "No provider is wired.",
        "No bars are loaded.",
        "No replay is executed.",
    ],
}

OUT.write_text(json.dumps(contract, indent=2))

TXT.write_text("\n".join([
    "HISTORICAL REPLAY MARKET DATA PROVIDER CONTRACT",
    f"Generated: {contract['generated_at']}",
    f"Schema: {contract['schema_id']}",
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
