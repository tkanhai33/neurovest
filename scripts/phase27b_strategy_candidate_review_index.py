#!/usr/bin/env python3
import json
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
CANDIDATES = ROOT / "runtime/strategy_candidates"
OUT = ROOT / "runtime/strategy_candidates/review_index_latest.json"
TXT = ROOT / "runtime/strategy_candidates/review_index_latest.txt"

CANDIDATES.mkdir(parents=True, exist_ok=True)

items = []

for path in sorted(CANDIDATES.glob("candidate_*.json")):
    try:
        data = json.loads(path.read_text())
    except Exception as error:
        items.append({
            "path": str(path),
            "status": "unreadable",
            "error": str(error),
        })
        continue

    proposal = str(data.get("assistant_proposal", ""))
    summary = proposal.replace("\n", " ").strip()
    if len(summary) > 280:
        summary = summary[:277] + "..."

    items.append({
        "candidate_id": data.get("candidate_id"),
        "path": str(path),
        "created_at": data.get("created_at"),
        "status": data.get("status"),
        "symbol": data.get("symbol"),
        "intent": data.get("intent"),
        "requires_user_approval": data.get("requires_user_approval") is True,
        "requires_sandbox_test": data.get("requires_sandbox_test") is True,
        "requires_promotion_review": data.get("requires_promotion_review") is True,
        "simulation_only": data.get("safety", {}).get("simulation_only") is True,
        "summary": summary,
    })

review_index = {
    "generated_at": datetime.now(UTC).isoformat(),
    "candidate_count": len(items),
    "pending_review_count": sum(1 for item in items if item.get("status") == "captured_pending_review"),
    "sandbox_ready_count": sum(
        1 for item in items
        if item.get("requires_sandbox_test") and item.get("simulation_only")
    ),
    "live_execution_allowed": False,
    "broker_execution_allowed": False,
    "items": items,
}

OUT.write_text(json.dumps(review_index, indent=2))

lines = [
    "STRATEGY CANDIDATE REVIEW INDEX",
    f"Generated: {review_index['generated_at']}",
    f"Candidates: {review_index['candidate_count']}",
    f"Pending Review: {review_index['pending_review_count']}",
    f"Sandbox Ready: {review_index['sandbox_ready_count']}",
    "",
]

for item in items:
    lines.extend([
        f"- {item.get('candidate_id')}",
        f"  Symbol: {item.get('symbol') or '—'}",
        f"  Status: {item.get('status')}",
        f"  Path: {item.get('path')}",
        f"  Summary: {item.get('summary')}",
        "",
    ])

TXT.write_text("\n".join(lines))

print(json.dumps({
    "status": "ok",
    "candidate_count": review_index["candidate_count"],
    "pending_review_count": review_index["pending_review_count"],
    "output_json": str(OUT),
    "output_txt": str(TXT),
}, indent=2))
