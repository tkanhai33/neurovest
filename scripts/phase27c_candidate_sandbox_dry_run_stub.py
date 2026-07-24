#!/usr/bin/env python3
import json
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
CANDIDATES = ROOT / "runtime/strategy_candidates"
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"
OUT = SANDBOX / "sandbox_dry_run_index_latest.json"
TXT = SANDBOX / "sandbox_dry_run_index_latest.txt"

SANDBOX.mkdir(parents=True, exist_ok=True)

review_path = CANDIDATES / "review_index_latest.json"

if not review_path.exists():
    raise SystemExit("Missing review index. Run Phase 27B first.")

review = json.loads(review_path.read_text())
items = review.get("items", [])

dry_runs = []

for item in items:
    candidate_id = item.get("candidate_id")
    if not candidate_id:
        continue

    result = {
        "candidate_id": candidate_id,
        "symbol": item.get("symbol"),
        "source_candidate_path": item.get("path"),
        "created_at": datetime.now(UTC).isoformat(),
        "sandbox_status": "dry_run_stub_created",
        "ready_for_sandbox": True,
        "simulation_status": "pending",
        "historical_replay_status": "not_started",
        "monte_carlo_status": "not_started",
        "score_status": "not_scored",
        "approval_status": "pending_user_review",
        "live_execution_allowed": False,
        "broker_execution_allowed": False,
        "writes_to_strategy_registry": False,
        "notes": [
            "Stub only. No backtest executed.",
            "Stub only. No strategy registry mutation.",
            "Stub only. No broker/live execution path.",
        ],
    }

    out_file = SANDBOX / f"{candidate_id}_sandbox_stub.json"
    out_file.write_text(json.dumps(result, indent=2))

    dry_runs.append({
        **result,
        "sandbox_stub_path": str(out_file),
    })

index = {
    "phase": "27C_CANDIDATE_SANDBOX_DRY_RUN_STUB",
    "generated_at": datetime.now(UTC).isoformat(),
    "candidate_count": len(dry_runs),
    "live_execution_allowed": False,
    "broker_execution_allowed": False,
    "writes_to_strategy_registry": False,
    "dry_runs": dry_runs,
}

OUT.write_text(json.dumps(index, indent=2))

lines = [
    "CANDIDATE SANDBOX DRY-RUN STUB INDEX",
    f"Generated: {index['generated_at']}",
    f"Candidates: {index['candidate_count']}",
    "Live Execution: LOCKED",
    "Broker Execution: LOCKED",
    "Strategy Registry Writes: DISABLED",
    "",
]

for item in dry_runs:
    lines.extend([
        f"- {item.get('candidate_id')}",
        f"  Symbol: {item.get('symbol') or '—'}",
        f"  Sandbox: {item.get('sandbox_status')}",
        f"  Simulation: {item.get('simulation_status')}",
        f"  Approval: {item.get('approval_status')}",
        f"  Path: {item.get('sandbox_stub_path')}",
        "",
    ])

TXT.write_text("\n".join(lines))

print(json.dumps({
    "status": "ok",
    "candidate_count": index["candidate_count"],
    "output_json": str(OUT),
    "output_txt": str(TXT),
}, indent=2))
