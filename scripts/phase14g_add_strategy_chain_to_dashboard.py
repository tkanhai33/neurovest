#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(".").resolve()
p = ROOT / "scripts/phase10g_architecture_drift_dashboard_summary.py"
text = p.read_text()

if "STRATEGY_SERVICE_CHAIN" not in text:
    text = text.replace(
        'PORTFOLIO_SERVICE_CHAIN = ROOT / "runtime/repo_memory/portfolio_service_chain_graph_v1.json"',
        'PORTFOLIO_SERVICE_CHAIN = ROOT / "runtime/repo_memory/portfolio_service_chain_graph_v1.json"\nSTRATEGY_SERVICE_CHAIN = ROOT / "runtime/repo_memory/strategy_service_chain_graph_v1.json"'
    )

if "strategy_service_chain = " not in text:
    text = text.replace(
        'portfolio_service_chain = json.loads(PORTFOLIO_SERVICE_CHAIN.read_text()) if PORTFOLIO_SERVICE_CHAIN.exists() else {}',
        'portfolio_service_chain = json.loads(PORTFOLIO_SERVICE_CHAIN.read_text()) if PORTFOLIO_SERVICE_CHAIN.exists() else {}\nstrategy_service_chain = json.loads(STRATEGY_SERVICE_CHAIN.read_text()) if STRATEGY_SERVICE_CHAIN.exists() else {}'
    )

if '"strategy_service_chain": {' not in text:
    text = text.replace(
'''    "portfolio_service_chain": {
        "node_count": portfolio_service_chain.get("node_count", 0),
        "edge_count": portfolio_service_chain.get("edge_count", 0),
        "nodes": portfolio_service_chain.get("nodes", []),
        "edges": portfolio_service_chain.get("edges", []),
    },
}''',
'''    "portfolio_service_chain": {
        "node_count": portfolio_service_chain.get("node_count", 0),
        "edge_count": portfolio_service_chain.get("edge_count", 0),
        "nodes": portfolio_service_chain.get("nodes", []),
        "edges": portfolio_service_chain.get("edges", []),
    },
    "strategy_service_chain": {
        "node_count": strategy_service_chain.get("node_count", 0),
        "edge_count": strategy_service_chain.get("edge_count", 0),
        "nodes": strategy_service_chain.get("nodes", []),
        "edges": strategy_service_chain.get("edges", []),
    },
}'''
    )

if "STRATEGY SERVICE CHAIN GRAPH" not in text:
    text = text.replace(
'''lines.append("")
lines.append("ARCHITECTURE DRIFT")''',
'''lines.append("")
lines.append("STRATEGY SERVICE CHAIN GRAPH")
lines.append("-" * 70)
lines.append(f"Nodes                : {dashboard['strategy_service_chain']['node_count']}")
lines.append(f"Edges                : {dashboard['strategy_service_chain']['edge_count']}")

for edge in dashboard["strategy_service_chain"]["edges"]:
    lines.append(f"{edge['from']} -> {edge['to']} :: {edge['type']}")

lines.append("")
lines.append("ARCHITECTURE DRIFT")'''
    )

p.write_text(text)
print("patched architecture dashboard with strategy service-chain graph")
