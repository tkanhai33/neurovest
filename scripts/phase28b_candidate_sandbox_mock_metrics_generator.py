#!/usr/bin/env python3
import json
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"
HARNESS = SANDBOX / "simulation_harness_stub_latest.json"
OUT = SANDBOX / "candidate_sandbox_mock_metrics_index_latest.json"
TXT = SANDBOX / "candidate_sandbox_mock_metrics_index_latest.txt"

if not HARNESS.exists():
    raise SystemExit("Missing 28A simulation harness stub.")

harness = json.loads(HARNESS.read_text())
items = harness.get("items", [])

mock_results = []

for index, item in enumerate(items, start=1):
    candidate_id = item.get("candidate_id")
    if not candidate_id:
        continue

    mock = {
        "candidate_id": candidate_id,
        "symbol": item.get("symbol"),
        "generated_at": datetime.now(UTC).isoformat(),
        "mock_only": True,
        "market_data_used": False,
        "backtest_executed": False,
        "simulation_executed": False,
        "historical_replay_executed": False,
        "monte_carlo_executed": False,
        "trade_count": 0,
        "win_rate": None,
        "profit_factor": None,
        "max_drawdown": None,
        "average_return": None,
        "confidence_score": None,
        "promotion_recommendation": "review_not_ready",
        "approval_required": True,
        "live_execution_allowed": False,
        "broker_execution_allowed": False,
        "writes_to_strategy_registry": False,
        "notes": [
            "Mock metrics shell only.",
            "No real market data used.",
            "No backtest executed.",
            "No simulation executed.",
            "No promotion allowed.",
        ],
    }

    out_file = SANDBOX / f"{candidate_id}_mock_metrics.json"
    out_file.write_text(json.dumps(mock, indent=2))

    mock_results.append({
        **mock,
        "mock_metrics_path": str(out_file),
        "mock_index": index,
    })

index_payload = {
    "phase": "28B_CANDIDATE_SANDBOX_MOCK_METRICS_GENERATOR",
    "generated_at": datetime.now(UTC).isoformat(),
    "mock_result_count": len(mock_results),
    "mock_only": True,
    "market_data_used": False,
    "backtest_executed": False,
    "simulation_executed": False,
    "promotion_allowed": False,
    "live_execution_allowed": False,
    "broker_execution_allowed": False,
    "writes_to_strategy_registry": False,
    "results": mock_results,
}

OUT.write_text(json.dumps(index_payload, indent=2))

lines = [
    "CANDIDATE SANDBOX MOCK METRICS INDEX",
    f"Generated: {index_payload['generated_at']}",
    f"Mock Results: {index_payload['mock_result_count']}",
    "Mock Only: TRUE",
    "Market Data Used: FALSE",
    "Backtest Executed: FALSE",
    "Simulation Executed: FALSE",
    "Promotion Allowed: FALSE",
    "Live Execution: LOCKED",
    "Broker Execution: LOCKED",
    "Strategy Registry Writes: DISABLED",
    "",
]

for item in mock_results:
    lines.extend([
        f"- {item.get('candidate_id')}",
        f"  Symbol: {item.get('symbol') or '—'}",
        f"  Trade Count: {item.get('trade_count')}",
        f"  Recommendation: {item.get('promotion_recommendation')}",
        f"  Path: {item.get('mock_metrics_path')}",
        "",
    ])

TXT.write_text("\n".join(lines))

print(json.dumps({
    "status": "ok",
    "mock_result_count": len(mock_results),
    "output_json": str(OUT),
    "output_txt": str(TXT),
}, indent=2))
