#!/usr/bin/env python3
import json
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"
OUT = SANDBOX / "simulation_harness_stub_latest.json"
TXT = SANDBOX / "simulation_harness_stub_latest.txt"

RESULT_STUB_INDEX = SANDBOX / "candidate_sandbox_result_stub_index_latest.json"

if not RESULT_STUB_INDEX.exists():
    raise SystemExit("Missing 27E result stub index.")

index = json.loads(RESULT_STUB_INDEX.read_text())
results = index.get("results", [])

harness_items = []

for item in results:
    candidate_id = item.get("candidate_id")
    if not candidate_id:
        continue

    harness_items.append({
        "candidate_id": candidate_id,
        "symbol": item.get("symbol"),
        "harness_status": "stub_ready",
        "simulation_mode": "dry_run_only",
        "simulation_execute_allowed": False,
        "historical_replay_execute_allowed": False,
        "monte_carlo_execute_allowed": False,
        "live_execution_allowed": False,
        "broker_execution_allowed": False,
        "writes_to_strategy_registry": False,
        "expected_inputs": {
            "candidate_file": item.get("source_sandbox_stub_path"),
            "result_stub_file": item.get("result_stub_path"),
            "market_data_source": "not_wired",
            "date_range": "not_wired",
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
        "notes": [
            "Harness stub only.",
            "No simulation executed.",
            "No historical replay executed.",
            "No Monte Carlo executed.",
            "No live/broker execution path enabled.",
        ],
    })

harness = {
    "phase": "28A_CANDIDATE_SANDBOX_SIMULATION_HARNESS_STUB",
    "generated_at": datetime.now(UTC).isoformat(),
    "candidate_count": len(harness_items),
    "harness_status": "stub_ready",
    "simulation_execute_allowed": False,
    "historical_replay_execute_allowed": False,
    "monte_carlo_execute_allowed": False,
    "live_execution_allowed": False,
    "broker_execution_allowed": False,
    "writes_to_strategy_registry": False,
    "items": harness_items,
}

OUT.write_text(json.dumps(harness, indent=2))

lines = [
    "CANDIDATE SANDBOX SIMULATION HARNESS STUB",
    f"Generated: {harness['generated_at']}",
    f"Candidates: {harness['candidate_count']}",
    "Simulation Execute: DISABLED",
    "Historical Replay Execute: DISABLED",
    "Monte Carlo Execute: DISABLED",
    "Live Execution: LOCKED",
    "Broker Execution: LOCKED",
    "Strategy Registry Writes: DISABLED",
    "",
]

for item in harness_items:
    lines.extend([
        f"- {item.get('candidate_id')}",
        f"  Symbol: {item.get('symbol') or '—'}",
        f"  Harness: {item.get('harness_status')}",
        f"  Mode: {item.get('simulation_mode')}",
        "",
    ])

TXT.write_text("\n".join(lines))

print(json.dumps({
    "status": "ok",
    "candidate_count": harness["candidate_count"],
    "output_json": str(OUT),
    "output_txt": str(TXT),
}, indent=2))
