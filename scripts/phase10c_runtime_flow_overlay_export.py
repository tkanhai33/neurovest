#!/usr/bin/env python3
import json
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/repo_memory/runtime_flow_overlay_v1.json"

RUNTIME_FLOW = [
    ("chat_public", "repo_memory"),
    ("repo_memory", "research_db"),
    ("research_db", "market_data"),
    ("market_data", "strategy"),
    ("strategy", "risk"),
    ("risk", "execution"),
    ("execution", "events_broker"),
    ("events_broker", "journal_ledger"),
    ("journal_ledger", "portfolio_accounting"),
    ("portfolio_accounting", "portfolio_reconciliation"),
    ("portfolio_reconciliation", "graph_live"),
]

STACK_MAP = {
    "chat_public": "chat_public",
    "repo_memory": "learning_research",
    "research_db": "learning_research",
    "market_data": "market_data",
    "strategy": "strategy",
    "risk": "risk",
    "execution": "execution",
    "events_broker": "events",
    "journal_ledger": "journal_ledger",
    "portfolio_accounting": "portfolio",
    "portfolio_reconciliation": "portfolio",
    "graph_live": "core",
}

edges = []
for i, (src, dst) in enumerate(RUNTIME_FLOW, start=1):
    edges.append({
        "step": i,
        "from_runtime": src,
        "to_runtime": dst,
        "from_stack": STACK_MAP.get(src),
        "to_stack": STACK_MAP.get(dst),
    })

report = {
    "phase": "10C_RUNTIME_FLOW_OVERLAY_EXPORT",
    "generated_at": datetime.now(UTC).isoformat(),
    "runtime_step_count": len(edges),
    "runtime_edges": edges,
}

OUT.write_text(json.dumps(report, indent=2))

print(json.dumps({
    "phase": report["phase"],
    "runtime_step_count": report["runtime_step_count"],
    "output": str(OUT),
}, indent=2))
