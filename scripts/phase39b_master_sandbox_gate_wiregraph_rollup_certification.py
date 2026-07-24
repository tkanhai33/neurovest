#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "39B_master_sandbox_gate_wiregraph_rollup_certification_latest.json"
PHASE = "39B_MASTER_SANDBOX_GATE_WIREGRAPH_ROLLUP_CERTIFICATION"

WIREGRAPH_JSON = SANDBOX / "39A_master_sandbox_gate_wiregraph_latest.json"
WIREGRAPH_MMD = SANDBOX / "39A_master_sandbox_gate_wiregraph_latest.mmd"

REQUIRED_NODES = {
    "Strategy Rule Enablement Gate Locked",
    "Trade Simulation Enablement Gate Locked",
    "Risk Gate Locked",
    "Broker Execution Disabled",
    "Live Execution Disabled",
}

REQUIRED_FALSE_BEHAVIORS = [
    "entry_generation",
    "exit_generation",
    "strategy_rule_enablement",
    "trade_simulation_enablement",
    "risk_gate_passed",
    "trade_simulation",
    "broker_execution",
    "live_execution",
]

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "wiregraph_json": str(WIREGRAPH_JSON),
    "wiregraph_mermaid": str(WIREGRAPH_MMD),
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    graph = json.loads(WIREGRAPH_JSON.read_text(encoding="utf-8")) if WIREGRAPH_JSON.exists() else {}

    nodes = set(graph.get("nodes", []))
    edges = graph.get("edges", [])
    behavior = graph.get("current_behavior", {})
    locks = graph.get("safety_locks", {})

    result["wiregraph_phase"] = graph.get("phase")
    result["node_count"] = len(nodes)
    result["edge_count"] = len(edges)
    result["required_nodes_present"] = sorted(REQUIRED_NODES.intersection(nodes))
    result["required_nodes_missing"] = sorted(REQUIRED_NODES.difference(nodes))

    result["checks"]["wiregraph_json_exists"] = WIREGRAPH_JSON.exists()
    result["checks"]["wiregraph_mermaid_exists"] = WIREGRAPH_MMD.exists()
    result["checks"]["wiregraph_certified"] = graph.get("certified") is True
    result["checks"]["required_nodes_present"] = REQUIRED_NODES.issubset(nodes)
    result["checks"]["edge_count_gt_zero"] = len(edges) > 0
    result["checks"]["all_required_behaviors_false"] = all(
        behavior.get(key) is False for key in REQUIRED_FALSE_BEHAVIORS
    )
    result["checks"]["historical_bars_fetch_true"] = behavior.get("historical_bars_fetch") is True
    result["checks"]["bar_iteration_true"] = behavior.get("bar_iteration") is True
    result["checks"]["bar_only_metrics_true"] = behavior.get("bar_only_metrics") is True
    result["checks"]["hold_pipeline_true"] = behavior.get("hold_pipeline") is True
    result["checks"]["safety_locks_false"] = all(v is False for v in locks.values())

    result["pipeline_summary"] = {
        "from": "39A_MASTER_SANDBOX_GATE_WIREGRAPH_REFRESH",
        "to": "39B_MASTER_SANDBOX_GATE_WIREGRAPH_ROLLUP_CERTIFICATION",
        "certified_capability": [
            "master sandbox dependency wiregraph exists",
            "strategy gate represented",
            "trade simulation gate represented",
            "risk gate represented",
            "broker/live disabled endpoints represented",
        ],
        "current_behavior": [
            "historical bars, bar iteration, bar-only metrics, and hold pipeline are visible",
            "entry generation disabled",
            "exit generation disabled",
            "strategy enablement disabled",
            "trade simulation disabled",
            "risk gate not passed",
            "broker/live execution disabled",
        ],
        "next_recommended_phase": "39C_HANDOFF_BUNDLE_REFRESH",
    }

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(json.dumps(result, indent=2))
print(f"\\nWROTE: {OUT}")
