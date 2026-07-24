#!/usr/bin/env python3
import json
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
DIFF = ROOT / "runtime/repo_memory/runtime_static_dependency_diff_v1.json"
OUT = ROOT / "runtime/repo_memory/runtime_static_diff_classification_v1.json"

diff = json.loads(DIFF.read_text())

EXPECTED_RUNTIME_ONLY = {
    ("chat_public", "learning_research"): "runtime_context_lookup",
    ("learning_research", "market_data"): "runtime_research_to_market_context",
    ("market_data", "strategy"): "runtime_signal_input_flow",
    ("strategy", "risk"): "runtime_safety_gate_flow",
    ("risk", "execution"): "runtime_execution_gate_flow",
    ("execution", "events"): "runtime_event_publication_flow",
    ("events", "journal_ledger"): "runtime_persistence_event_flow",
    ("journal_ledger", "portfolio"): "runtime_accounting_refresh_flow",
    ("portfolio", "core"): "runtime_graph_state_refresh_flow",
}

EXPECTED_STATIC_ONLY = {
    ("strategy", "market_data"): "strategy_imports_market_data_helpers",
    ("strategy", "portfolio"): "strategy_imports_portfolio_helpers",
    ("portfolio", "market_data"): "portfolio_imports_market_data_helpers",
    ("learning_research", "db_model"): "research_imports_persistence_models",
}

classified_runtime_only = []
classified_static_only = []
classified_shared = []

drift_edges = []

for edge in diff.get("runtime_only_edges", []):
    pair = (edge["from"], edge["to"])
    reason = EXPECTED_RUNTIME_ONLY.get(pair)

    item = {
        "from": pair[0],
        "to": pair[1],
        "classification": "expected_runtime_only" if reason else "possible_runtime_drift",
        "reason": reason or "runtime edge has no expected classification",
    }

    classified_runtime_only.append(item)

    if not reason:
        drift_edges.append(item)

for edge in diff.get("static_only_edges", []):
    pair = (edge["from"], edge["to"])
    reason = EXPECTED_STATIC_ONLY.get(pair)

    item = {
        "from": pair[0],
        "to": pair[1],
        "classification": "expected_static_only" if reason else "possible_static_drift",
        "reason": reason or "static edge has no expected classification",
    }

    classified_static_only.append(item)

    if not reason:
        drift_edges.append(item)

for edge in diff.get("shared_edges", []):
    classified_shared.append({
        "from": edge["from"],
        "to": edge["to"],
        "classification": "shared_runtime_and_static",
        "reason": "edge appears in both runtime and static graphs",
    })

report = {
    "phase": "10E_CLASSIFY_RUNTIME_STATIC_DIFF_EDGES",
    "generated_at": datetime.now(UTC).isoformat(),
    "runtime_only_count": len(classified_runtime_only),
    "static_only_count": len(classified_static_only),
    "shared_count": len(classified_shared),
    "drift_count": len(drift_edges),
    "drift_edges": drift_edges,
    "classified_runtime_only": classified_runtime_only,
    "classified_static_only": classified_static_only,
    "classified_shared": classified_shared,
}

OUT.write_text(json.dumps(report, indent=2))

print(json.dumps({
    "phase": report["phase"],
    "runtime_only_count": report["runtime_only_count"],
    "static_only_count": report["static_only_count"],
    "shared_count": report["shared_count"],
    "drift_count": report["drift_count"],
    "output": str(OUT),
}, indent=2))
