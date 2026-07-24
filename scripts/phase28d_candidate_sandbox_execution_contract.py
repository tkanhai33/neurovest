#!/usr/bin/env python3
import json
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "candidate_sandbox_execution_contract_v1.json"
TXT = SANDBOX / "candidate_sandbox_execution_contract_v1.txt"

SANDBOX.mkdir(parents=True, exist_ok=True)

contract = {
    "phase": "28D_CANDIDATE_SANDBOX_EXECUTION_CONTRACT",
    "generated_at": datetime.now(UTC).isoformat(),
    "schema_id": "candidate_sandbox_execution_contract_v1",

    "inputs": {
        "candidate_file": "string",
        "date_range": "string",
        "capital": "number",
        "market_data_provider": "string",
    },

    "outputs": {
        "trade_count": "integer",
        "win_rate": "number|null",
        "profit_factor": "number|null",
        "max_drawdown": "number|null",
        "average_return": "number|null",
        "confidence_score": "number|null",
        "promotion_recommendation": "string|null",
    },

    "execution_flags": {
        "simulation_enabled": False,
        "historical_replay_enabled": False,
        "monte_carlo_enabled": False,
        "market_data_enabled": False,
        "promotion_enabled": False,
        "live_execution_enabled": False,
        "broker_execution_enabled": False,
        "registry_write_enabled": False,
    },

    "notes": [
        "Contract only.",
        "No sandbox execution performed.",
        "No market data wiring.",
        "No historical replay.",
        "No Monte Carlo execution.",
        "No promotion path enabled.",
        "No live execution path enabled.",
    ],
}

OUT.write_text(json.dumps(contract, indent=2))

lines = [
    "CANDIDATE SANDBOX EXECUTION CONTRACT",
    f"Generated: {contract['generated_at']}",
    f"Schema: {contract['schema_id']}",
    "",
    "Simulation Enabled: FALSE",
    "Historical Replay Enabled: FALSE",
    "Monte Carlo Enabled: FALSE",
    "Market Data Enabled: FALSE",
    "Promotion Enabled: FALSE",
    "Live Execution Enabled: FALSE",
    "Broker Execution Enabled: FALSE",
    "Registry Write Enabled: FALSE",
]

TXT.write_text("\n".join(lines))

print(json.dumps({
    "status": "ok",
    "contract_json": str(OUT),
    "contract_txt": str(TXT),
}, indent=2))
