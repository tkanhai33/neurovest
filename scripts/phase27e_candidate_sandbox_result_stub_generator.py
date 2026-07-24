#!/usr/bin/env python3
import json
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"
STUB_INDEX = SANDBOX / "sandbox_dry_run_index_latest.json"
SCHEMA = SANDBOX / "candidate_sandbox_result_schema_v1.json"
OUT_INDEX = SANDBOX / "candidate_sandbox_result_stub_index_latest.json"
OUT_TXT = SANDBOX / "candidate_sandbox_result_stub_index_latest.txt"

if not STUB_INDEX.exists():
    raise SystemExit("Missing 27C sandbox dry-run index.")

if not SCHEMA.exists():
    raise SystemExit("Missing 27D sandbox result schema.")

sandbox = json.loads(STUB_INDEX.read_text())
schema = json.loads(SCHEMA.read_text())

results = []

for item in sandbox.get("dry_runs", []):
    candidate_id = item.get("candidate_id")
    if not candidate_id:
        continue

    result = {
        "schema_id": schema.get("schema_id"),
        "candidate_id": candidate_id,
        "symbol": item.get("symbol"),
        "created_at": datetime.now(UTC).isoformat(),
        "simulation_status": "pending",
        "trade_count": 0,
        "win_rate": None,
        "profit_factor": None,
        "max_drawdown": None,
        "average_return": None,
        "confidence_score": None,
        "promotion_recommendation": None,
        "approval_required": True,
        "live_execution_allowed": False,
        "broker_execution_allowed": False,
        "writes_to_strategy_registry": False,
        "source_sandbox_stub_path": item.get("sandbox_stub_path"),
        "notes": [
            "Result stub only.",
            "No backtest executed.",
            "No live execution.",
            "No broker execution.",
            "No strategy registry mutation.",
        ],
    }

    out_file = SANDBOX / f"{candidate_id}_sandbox_result_stub.json"
    out_file.write_text(json.dumps(result, indent=2))

    results.append({
        **result,
        "result_stub_path": str(out_file),
    })

index = {
    "phase": "27E_CANDIDATE_SANDBOX_RESULT_STUB_GENERATOR",
    "generated_at": datetime.now(UTC).isoformat(),
    "schema_id": schema.get("schema_id"),
    "result_count": len(results),
    "simulation_status": "pending",
    "live_execution_allowed": False,
    "broker_execution_allowed": False,
    "writes_to_strategy_registry": False,
    "results": results,
}

OUT_INDEX.write_text(json.dumps(index, indent=2))

lines = [
    "CANDIDATE SANDBOX RESULT STUB INDEX",
    f"Generated: {index['generated_at']}",
    f"Results: {index['result_count']}",
    "Simulation: PENDING",
    "Live Execution: LOCKED",
    "Broker Execution: LOCKED",
    "Strategy Registry Writes: DISABLED",
    "",
]

for item in results:
    lines.extend([
        f"- {item.get('candidate_id')}",
        f"  Symbol: {item.get('symbol') or '—'}",
        f"  Status: {item.get('simulation_status')}",
        f"  Trades: {item.get('trade_count')}",
        f"  Path: {item.get('result_stub_path')}",
        "",
    ])

OUT_TXT.write_text("\n".join(lines))

print(json.dumps({
    "status": "ok",
    "result_count": len(results),
    "output_json": str(OUT_INDEX),
    "output_txt": str(OUT_TXT),
}, indent=2))
