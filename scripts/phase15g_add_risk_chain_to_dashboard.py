#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(".").resolve()
p = ROOT / "scripts/phase10g_architecture_drift_dashboard_summary.py"
text = p.read_text()

if "RISK_SERVICE_CHAIN" not in text:
    text = text.replace(
        'STRATEGY_SERVICE_CHAIN = ROOT / "runtime/repo_memory/strategy_service_chain_graph_v1.json"',
        'STRATEGY_SERVICE_CHAIN = ROOT / "runtime/repo_memory/strategy_service_chain_graph_v1.json"\nRISK_SERVICE_CHAIN = ROOT / "runtime/repo_memory/risk_service_chain_graph_v1.json"'
    )

if "risk_service_chain = " not in text:
    text = text.replace(
        'strategy_service_chain = json.loads(STRATEGY_SERVICE_CHAIN.read_text()) if STRATEGY_SERVICE_CHAIN.exists() else {}',
        'strategy_service_chain = json.loads(STRATEGY_SERVICE_CHAIN.read_text()) if STRATEGY_SERVICE_CHAIN.exists() else {}\nrisk_service_chain = json.loads(RISK_SERVICE_CHAIN.read_text()) if RISK_SERVICE_CHAIN.exists() else {}'
    )

if '"risk_service_chain": {' not in text:
    text = text.replace(
'''    "strategy_service_chain": {
        "node_count": strategy_service_chain.get("node_count", 0),
        "edge_count": strategy_service_chain.get("edge_count", 0),
        "nodes": strategy_service_chain.get("nodes", []),
        "edges": strategy_service_chain.get("edges", []),
    },
}''',
'''    "strategy_service_chain": {
        "node_count": strategy_service_chain.get("node_count", 0),
        "edge_count": strategy_service_chain.get("edge_count", 0),
        "nodes": strategy_service_chain.get("nodes", []),
        "edges": strategy_service_chain.get("edges", []),
    },
    "risk_service_chain": {
        "node_count": risk_service_chain.get("node_count", 0),
        "edge_count": risk_service_chain.get("edge_count", 0),
        "nodes": risk_service_chain.get("nodes", []),
        "edges": risk_service_chain.get("edges", []),
    },
}'''
    )

if "RISK SERVICE CHAIN GRAPH" not in text:
    text = text.replace(
'''lines.append("")
lines.append("ARCHITECTURE DRIFT")''',
'''lines.append("")
lines.append("RISK SERVICE CHAIN GRAPH")
lines.append("-" * 70)
lines.append(f"Nodes                : {dashboard['risk_service_chain']['node_count']}")
lines.append(f"Edges                : {dashboard['risk_service_chain']['edge_count']}")

for edge in dashboard["risk_service_chain"]["edges"]:
    lines.append(f"{edge['from']} -> {edge['to']} :: {edge['type']}")

lines.append("")
lines.append("ARCHITECTURE DRIFT")'''
    )

p.write_text(text)
print("patched architecture dashboard with risk service-chain graph")
