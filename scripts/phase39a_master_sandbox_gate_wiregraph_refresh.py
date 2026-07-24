#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"
SANDBOX.mkdir(parents=True, exist_ok=True)

OUT_JSON = SANDBOX / "39A_master_sandbox_gate_wiregraph_latest.json"
OUT_MMD = SANDBOX / "39A_master_sandbox_gate_wiregraph_latest.mmd"

PHASE = "39A_MASTER_SANDBOX_GATE_WIREGRAPH_REFRESH"

locks = {
    "live_execution_enabled": False,
    "broker_execution_enabled": False,
    "historical_replay_enabled": False,
    "simulation_enabled": False,
    "registry_write_enabled": False,
    "promotion_enabled": False,
    "learning_enabled": False,
}

nodes = [
    "Chat Strategy Proposal Capture",
    "Strategy Candidate Index",
    "Historical Bars Adapter yfinance",
    "Historical Bars Validation",
    "Bar Iterator",

    "Bar Only Metrics",
    "Candidate Scorecard",
    "Manual Promotion Gate Blocked",

    "Hold Signal Generator",
    "Hold Decision Engine",
    "Hold Event Bridge",

    "Entry Rule Contract Disabled",
    "Entry Rule Validator",
    "Entry Signal Generator Disabled",

    "Exit Rule Contract Disabled",
    "Exit Rule Validator",
    "Exit Signal Generator Disabled",

    "Strategy Rule Enablement Gate Locked",
    "Trade Simulation Enablement Gate Locked",
    "Risk Gate Locked",

    "Trade Simulation Contract Disabled",
    "Trade Event Validator",
    "Broker Execution Disabled",
    "Live Execution Disabled",
]

edges = [
    ["Chat Strategy Proposal Capture", "Strategy Candidate Index"],
    ["Strategy Candidate Index", "Historical Bars Adapter yfinance"],
    ["Historical Bars Adapter yfinance", "Historical Bars Validation"],
    ["Historical Bars Validation", "Bar Iterator"],

    ["Bar Iterator", "Bar Only Metrics"],
    ["Bar Only Metrics", "Candidate Scorecard"],
    ["Candidate Scorecard", "Manual Promotion Gate Blocked"],

    ["Bar Iterator", "Hold Signal Generator"],
    ["Hold Signal Generator", "Hold Decision Engine"],
    ["Hold Decision Engine", "Hold Event Bridge"],

    ["Bar Iterator", "Entry Rule Contract Disabled"],
    ["Entry Rule Contract Disabled", "Entry Rule Validator"],
    ["Entry Rule Validator", "Entry Signal Generator Disabled"],

    ["Bar Iterator", "Exit Rule Contract Disabled"],
    ["Exit Rule Contract Disabled", "Exit Rule Validator"],
    ["Exit Rule Validator", "Exit Signal Generator Disabled"],

    ["Manual Promotion Gate Blocked", "Strategy Rule Enablement Gate Locked"],
    ["Entry Signal Generator Disabled", "Strategy Rule Enablement Gate Locked"],
    ["Exit Signal Generator Disabled", "Strategy Rule Enablement Gate Locked"],

    ["Strategy Rule Enablement Gate Locked", "Trade Simulation Enablement Gate Locked"],
    ["Risk Gate Locked", "Trade Simulation Enablement Gate Locked"],

    ["Trade Simulation Enablement Gate Locked", "Trade Simulation Contract Disabled"],
    ["Trade Simulation Contract Disabled", "Trade Event Validator"],

    ["Trade Event Validator", "Broker Execution Disabled"],
    ["Broker Execution Disabled", "Live Execution Disabled"],
]

def node_id(name: str) -> str:
    return (
        name.lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("/", "_")
    )

mmd = [
    "flowchart TD",
    "  classDef certified fill:#ecfff1,stroke:#008833,stroke-width:1px;",
    "  classDef locked fill:#ffecec,stroke:#aa0000,stroke-width:1px;",
    "  classDef gate fill:#fff7e6,stroke:#cc7700,stroke-width:2px;",
]

for node in nodes:
    if "Gate" in node:
        cls = "gate"
    elif "Disabled" in node or "Blocked" in node or "Locked" in node:
        cls = "locked"
    else:
        cls = "certified"
    mmd.append(f'  {node_id(node)}["{node}"]:::{cls}')

for src, dst in edges:
    mmd.append(f"  {node_id(src)} --> {node_id(dst)}")

graph = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "stage": "Master sandbox gate dependency wiregraph refreshed",
    "nodes": nodes,
    "edges": [{"from": a, "to": b} for a, b in edges],
    "safety_locks": locks,
    "current_behavior": {
        "historical_bars_fetch": True,
        "bar_iteration": True,
        "bar_only_metrics": True,
        "scorecard_review_only": True,
        "hold_pipeline": True,
        "entry_generation": False,
        "exit_generation": False,
        "strategy_rule_enablement": False,
        "trade_simulation_enablement": False,
        "risk_gate_passed": False,
        "trade_simulation": False,
        "broker_execution": False,
        "live_execution": False,
    },
    "outputs": {
        "json": str(OUT_JSON),
        "mermaid": str(OUT_MMD),
    },
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    graph["checks"]["node_count_gt_zero"] = len(nodes) > 0
    graph["checks"]["edge_count_gt_zero"] = len(edges) > 0
    graph["checks"]["all_edges_reference_existing_nodes"] = all(a in nodes and b in nodes for a, b in edges)
    graph["checks"]["strategy_gate_present"] = "Strategy Rule Enablement Gate Locked" in nodes
    graph["checks"]["trade_sim_gate_present"] = "Trade Simulation Enablement Gate Locked" in nodes
    graph["checks"]["risk_gate_present"] = "Risk Gate Locked" in nodes
    graph["checks"]["broker_disabled_present"] = "Broker Execution Disabled" in nodes
    graph["checks"]["live_disabled_present"] = "Live Execution Disabled" in nodes
    graph["checks"]["entry_generation_false"] = graph["current_behavior"]["entry_generation"] is False
    graph["checks"]["exit_generation_false"] = graph["current_behavior"]["exit_generation"] is False
    graph["checks"]["trade_simulation_false"] = graph["current_behavior"]["trade_simulation"] is False
    graph["checks"]["broker_execution_false"] = graph["current_behavior"]["broker_execution"] is False
    graph["checks"]["live_execution_false"] = graph["current_behavior"]["live_execution"] is False
    graph["checks"]["safety_locks_false"] = all(v is False for v in locks.values())

    graph["certified"] = all(graph["checks"].values())

except Exception as exc:
    graph["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT_JSON.write_text(json.dumps(graph, indent=2), encoding="utf-8")
OUT_MMD.write_text("\\n".join(mmd) + "\\n", encoding="utf-8")

print(json.dumps(graph, indent=2))
print(f"\\nWROTE JSON: {OUT_JSON}")
print(f"WROTE MMD:  {OUT_MMD}")
