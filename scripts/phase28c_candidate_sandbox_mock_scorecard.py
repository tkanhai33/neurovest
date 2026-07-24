#!/usr/bin/env python3
import json
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"
MOCK = SANDBOX / "candidate_sandbox_mock_metrics_index_latest.json"
OUT = SANDBOX / "candidate_sandbox_mock_scorecard_latest.json"
TXT = SANDBOX / "candidate_sandbox_mock_scorecard_latest.txt"

if not MOCK.exists():
    raise SystemExit("Missing 28B mock metrics index.")

mock_index = json.loads(MOCK.read_text())
results = mock_index.get("results", [])

scorecards = []

for item in results:
    candidate_id = item.get("candidate_id")
    if not candidate_id:
        continue

    scorecard = {
        "candidate_id": candidate_id,
        "symbol": item.get("symbol"),
        "generated_at": datetime.now(UTC).isoformat(),
        "scorecard_status": "review_not_ready",
        "score": None,
        "confidence_score": None,
        "reason": "mock metrics only",
        "promotion_recommendation": "blocked",
        "approval_required": True,
        "mock_only": True,
        "market_data_used": False,
        "backtest_executed": False,
        "simulation_executed": False,
        "promotion_allowed": False,
        "live_execution_allowed": False,
        "broker_execution_allowed": False,
        "writes_to_strategy_registry": False,
        "source_mock_metrics_path": item.get("mock_metrics_path"),
        "notes": [
            "Scorecard is mock-only.",
            "No real metrics available yet.",
            "Promotion is blocked until real sandbox execution is certified.",
        ],
    }

    out_file = SANDBOX / f"{candidate_id}_mock_scorecard.json"
    out_file.write_text(json.dumps(scorecard, indent=2))

    scorecards.append({
        **scorecard,
        "scorecard_path": str(out_file),
    })

index = {
    "phase": "28C_CANDIDATE_SANDBOX_MOCK_SCORECARD",
    "generated_at": datetime.now(UTC).isoformat(),
    "scorecard_count": len(scorecards),
    "scorecard_status": "review_not_ready",
    "reason": "mock metrics only",
    "promotion_allowed": False,
    "live_execution_allowed": False,
    "broker_execution_allowed": False,
    "writes_to_strategy_registry": False,
    "scorecards": scorecards,
}

OUT.write_text(json.dumps(index, indent=2))

lines = [
    "CANDIDATE SANDBOX MOCK SCORECARD",
    f"Generated: {index['generated_at']}",
    f"Scorecards: {index['scorecard_count']}",
    "Status: REVIEW_NOT_READY",
    "Reason: mock metrics only",
    "Promotion: BLOCKED",
    "Live Execution: LOCKED",
    "Broker Execution: LOCKED",
    "Strategy Registry Writes: DISABLED",
    "",
]

for item in scorecards:
    lines.extend([
        f"- {item.get('candidate_id')}",
        f"  Symbol: {item.get('symbol') or '—'}",
        f"  Status: {item.get('scorecard_status')}",
        f"  Score: {item.get('score')}",
        f"  Reason: {item.get('reason')}",
        f"  Promotion: {item.get('promotion_recommendation')}",
        f"  Path: {item.get('scorecard_path')}",
        "",
    ])

TXT.write_text("\n".join(lines))

print(json.dumps({
    "status": "ok",
    "scorecard_count": len(scorecards),
    "output_json": str(OUT),
    "output_txt": str(TXT),
}, indent=2))
