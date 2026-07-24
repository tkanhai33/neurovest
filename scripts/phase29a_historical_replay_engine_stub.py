#!/usr/bin/env python3
import json
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"
CONTRACT = SANDBOX / "candidate_sandbox_execution_contract_v1.json"
OUT = SANDBOX / "historical_replay_engine_stub_latest.json"
TXT = SANDBOX / "historical_replay_engine_stub_latest.txt"

if not CONTRACT.exists():
    raise SystemExit("Missing 28D execution contract.")

contract = json.loads(CONTRACT.read_text())
flags = contract.get("execution_flags", {})

stub = {
    "phase": "29A_HISTORICAL_REPLAY_ENGINE_STUB",
    "generated_at": datetime.now(UTC).isoformat(),
    "engine_status": "stub_only",
    "contract_schema_id": contract.get("schema_id"),
    "historical_replay_enabled": False,
    "historical_replay_execute_allowed": False,
    "market_data_enabled": False,
    "simulation_enabled": False,
    "monte_carlo_enabled": False,
    "promotion_enabled": False,
    "live_execution_enabled": False,
    "broker_execution_enabled": False,
    "registry_write_enabled": False,
    "expected_inputs": {
        "candidate_file": "string",
        "historical_bars": "not_wired",
        "date_range": "not_wired",
        "capital": "not_wired",
    },
    "expected_outputs": {
        "trade_count": 0,
        "win_rate": None,
        "profit_factor": None,
        "max_drawdown": None,
        "average_return": None,
        "confidence_score": None,
        "promotion_recommendation": None,
    },
    "source_contract_flags": flags,
    "notes": [
        "Historical replay engine stub only.",
        "No bars loaded.",
        "No trades simulated.",
        "No metrics calculated.",
        "No promotion path enabled.",
        "No live or broker execution enabled.",
    ],
}

OUT.write_text(json.dumps(stub, indent=2))

TXT.write_text("\n".join([
    "HISTORICAL REPLAY ENGINE STUB",
    f"Generated: {stub['generated_at']}",
    "Engine Status: STUB ONLY",
    "Historical Replay Enabled: FALSE",
    "Market Data Enabled: FALSE",
    "Simulation Enabled: FALSE",
    "Monte Carlo Enabled: FALSE",
    "Promotion Enabled: FALSE",
    "Live Execution Enabled: FALSE",
    "Broker Execution Enabled: FALSE",
    "Registry Write Enabled: FALSE",
]))

print(json.dumps({
    "status": "ok",
    "output_json": str(OUT),
    "output_txt": str(TXT),
}, indent=2))
