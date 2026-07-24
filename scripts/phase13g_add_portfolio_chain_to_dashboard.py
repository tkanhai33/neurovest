#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(".").resolve()
p = ROOT / "scripts/phase10g_architecture_drift_dashboard_summary.py"
text = p.read_text()

if "PORTFOLIO_SERVICE_CHAIN" not in text:
    text = text.replace(
        'SERVICE_CHAIN = ROOT / "runtime/repo_memory/service_chain_graph_v1.json"',
        'SERVICE_CHAIN = ROOT / "runtime/repo_memory/service_chain_graph_v1.json"\nPORTFOLIO_SERVICE_CHAIN = ROOT / "runtime/repo_memory/portfolio_service_chain_graph_v1.json"'
    )

if "portfolio_service_chain = " not in text:
    text = text.replace(
        'service_chain = json.loads(SERVICE_CHAIN.read_text()) if SERVICE_CHAIN.exists() else {}',
        'service_chain = json.loads(SERVICE_CHAIN.read_text()) if SERVICE_CHAIN.exists() else {}\nportfolio_service_chain = json.loads(PORTFOLIO_SERVICE_CHAIN.read_text()) if PORTFOLIO_SERVICE_CHAIN.exists() else {}'
    )

if '"portfolio_service_chain": {' not in text:
    text = text.replace(
'''    "service_chain": {
        "node_count": service_chain.get("node_count", 0),
        "edge_count": service_chain.get("edge_count", 0),
        "nodes": service_chain.get("nodes", []),
        "edges": service_chain.get("edges", []),
    },
}''',
'''    "service_chain": {
        "node_count": service_chain.get("node_count", 0),
        "edge_count": service_chain.get("edge_count", 0),
        "nodes": service_chain.get("nodes", []),
        "edges": service_chain.get("edges", []),
    },
    "portfolio_service_chain": {
        "node_count": portfolio_service_chain.get("node_count", 0),
        "edge_count": portfolio_service_chain.get("edge_count", 0),
        "nodes": portfolio_service_chain.get("nodes", []),
        "edges": portfolio_service_chain.get("edges", []),
    },
}'''
    )

if "PORTFOLIO SERVICE CHAIN GRAPH" not in text:
    text = text.replace(
'''lines.append("")
lines.append("ARCHITECTURE DRIFT")''',
'''lines.append("")
lines.append("PORTFOLIO SERVICE CHAIN GRAPH")
lines.append("-" * 70)
lines.append(f"Nodes                : {dashboard['portfolio_service_chain']['node_count']}")
lines.append(f"Edges                : {dashboard['portfolio_service_chain']['edge_count']}")

for edge in dashboard["portfolio_service_chain"]["edges"]:
    lines.append(f"{edge['from']} -> {edge['to']} :: {edge['type']}")

lines.append("")
lines.append("ARCHITECTURE DRIFT")'''
    )

p.write_text(text)
print("patched architecture dashboard with portfolio service-chain graph")
