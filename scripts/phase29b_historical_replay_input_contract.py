#!/usr/bin/env python3
import json
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"
OUT = SANDBOX / "historical_replay_input_contract_v1.json"
TXT = SANDBOX / "historical_replay_input_contract_v1.txt"

SANDBOX.mkdir(parents=True, exist_ok=True)

contract = {
    "phase": "29B_HISTORICAL_REPLAY_INPUT_CONTRACT",
    "generated_at": datetime.now(UTC).isoformat(),
    "schema_id": "historical_replay_input_contract_v1",
    "required_inputs": {
        "candidate_id": "string",
        "candidate_file": "string",
        "symbol": "string|null",
        "start_date": "YYYY-MM-DD",
        "end_date": "YYYY-MM-DD",
        "initial_capital": "number",
        "bar_interval": "1d|1h|15m|5m",
        "market_data_provider": "not_wired",
    },
    "optional_inputs": {
        "max_trades": "integer|null",
        "commission_model": "none|flat|percent",
        "slippage_model": "none|fixed_bps",
        "risk_profile": "conservative|balanced|aggressive|null",
    },
    "execution_flags": {
        "historical_replay_enabled": False,
        "market_data_enabled": False,
        "simulation_enabled": False,
        "live_execution_enabled": False,
        "broker_execution_enabled": False,
        "registry_write_enabled": False,
    },
    "validation_rules": [
        "candidate_file must exist before replay can run",
        "symbol must resolve before replay can run",
        "start_date must be before end_date",
        "initial_capital must be greater than zero",
        "market data provider must be certified before replay can run",
    ],
    "notes": [
        "Input contract only.",
        "No market data loaded.",
        "No historical replay executed.",
        "No trades simulated.",
    ],
}

OUT.write_text(json.dumps(contract, indent=2))

TXT.write_text("\n".join([
    "HISTORICAL REPLAY INPUT CONTRACT",
    f"Generated: {contract['generated_at']}",
    f"Schema: {contract['schema_id']}",
    "Historical Replay Enabled: FALSE",
    "Market Data Enabled: FALSE",
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
