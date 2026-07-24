#!/usr/bin/env python3
import json
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"
OUT = SANDBOX / "historical_replay_provider_adapter_stub_latest.json"
TXT = SANDBOX / "historical_replay_provider_adapter_stub_latest.txt"

CONTRACT = SANDBOX / "historical_replay_market_data_provider_contract_v1.json"

if not CONTRACT.exists():
    raise SystemExit("Missing 29E market data provider contract.")

contract = json.loads(CONTRACT.read_text())

adapter = {
    "phase": "29F_HISTORICAL_REPLAY_PROVIDER_ADAPTER_STUB",
    "generated_at": datetime.now(UTC).isoformat(),
    "adapter_status": "stub_only",
    "source_contract_schema": contract.get("schema_id"),
    "adapter_name": "historical_replay_provider_adapter_stub",
    "required_function": "get_historical_bars",
    "provider_wired": False,
    "market_data_enabled": False,
    "historical_replay_enabled": False,
    "simulation_enabled": False,
    "live_execution_enabled": False,
    "broker_execution_enabled": False,
    "registry_write_enabled": False,
    "stub_response_shape": {
        "symbol": None,
        "provider": "stub_not_wired",
        "bars": [],
        "bar_count": 0,
        "status": "not_wired",
        "error": "provider_adapter_stub_only",
    },
    "notes": [
        "Adapter stub only.",
        "No provider imported.",
        "No bars loaded.",
        "No replay executed.",
        "No live/broker path enabled.",
    ],
}

OUT.write_text(json.dumps(adapter, indent=2))

TXT.write_text("\n".join([
    "HISTORICAL REPLAY PROVIDER ADAPTER STUB",
    f"Generated: {adapter['generated_at']}",
    "Adapter Status: STUB ONLY",
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
    "adapter_json": str(OUT),
    "adapter_txt": str(TXT),
}, indent=2))
