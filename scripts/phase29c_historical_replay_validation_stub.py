#!/usr/bin/env python3
import json
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"
CONTRACT = SANDBOX / "historical_replay_input_contract_v1.json"
CANDIDATES = ROOT / "runtime/strategy_candidates/review_index_latest.json"

OUT = SANDBOX / "historical_replay_validation_stub_latest.json"
TXT = SANDBOX / "historical_replay_validation_stub_latest.txt"

if not CONTRACT.exists():
    raise SystemExit("Missing 29B historical replay input contract.")

contract = json.loads(CONTRACT.read_text())
candidates = json.loads(CANDIDATES.read_text()) if CANDIDATES.exists() else {"items": []}

items = []

for candidate in candidates.get("items", []):
    candidate_id = candidate.get("candidate_id")
    candidate_file = candidate.get("path")
    symbol = candidate.get("symbol")

    validation = {
        "candidate_id": candidate_id,
        "candidate_file": candidate_file,
        "symbol": symbol,
        "validation_status": "stub_validated_pending_execution",
        "candidate_file_exists": Path(candidate_file).exists() if candidate_file else False,
        "symbol_present": bool(symbol),
        "date_range_validated": False,
        "initial_capital_validated": False,
        "bar_interval_validated": False,
        "market_data_provider_certified": False,
        "ready_for_replay_execution": False,
        "historical_replay_enabled": False,
        "market_data_enabled": False,
        "simulation_enabled": False,
        "live_execution_enabled": False,
        "broker_execution_enabled": False,
        "registry_write_enabled": False,
        "notes": [
            "Validation stub only.",
            "No historical replay executed.",
            "No market data loaded.",
            "No trades simulated.",
        ],
    }

    items.append(validation)

index = {
    "phase": "29C_HISTORICAL_REPLAY_VALIDATION_STUB",
    "generated_at": datetime.now(UTC).isoformat(),
    "schema_id": "historical_replay_validation_stub_v1",
    "source_contract_schema": contract.get("schema_id"),
    "candidate_count": len(items),
    "ready_for_replay_count": 0,
    "historical_replay_enabled": False,
    "market_data_enabled": False,
    "simulation_enabled": False,
    "live_execution_enabled": False,
    "broker_execution_enabled": False,
    "registry_write_enabled": False,
    "items": items,
}

OUT.write_text(json.dumps(index, indent=2))

lines = [
    "HISTORICAL REPLAY VALIDATION STUB",
    f"Generated: {index['generated_at']}",
    f"Candidates: {index['candidate_count']}",
    "Ready For Replay: 0",
    "Historical Replay Enabled: FALSE",
    "Market Data Enabled: FALSE",
    "Simulation Enabled: FALSE",
    "Live Execution Enabled: FALSE",
    "Broker Execution Enabled: FALSE",
    "Registry Write Enabled: FALSE",
    "",
]

for item in items:
    lines.extend([
        f"- {item.get('candidate_id')}",
        f"  Symbol: {item.get('symbol') or '—'}",
        f"  Candidate File Exists: {item.get('candidate_file_exists')}",
        f"  Symbol Present: {item.get('symbol_present')}",
        f"  Ready For Replay: {item.get('ready_for_replay_execution')}",
        "",
    ])

TXT.write_text("\n".join(lines))

print(json.dumps({
    "status": "ok",
    "candidate_count": len(items),
    "output_json": str(OUT),
    "output_txt": str(TXT),
}, indent=2))
