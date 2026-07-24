#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(".").resolve()
p = ROOT / "scripts/phase10g_architecture_drift_dashboard_summary.py"
text = p.read_text()

text = text.replace(
'''HOTSPOTS = ROOT / "runtime/repo_memory/component_overlay_v1.json"
''',
'''HOTSPOTS = ROOT / "runtime/repo_memory/component_overlay_v1.json"
SERVICE_CHAIN = ROOT / "runtime/repo_memory/service_chain_graph_v1.json"
'''
)

text = text.replace(
'''hotspots = json.loads(HOTSPOTS.read_text()) if HOTSPOTS.exists() else {}
''',
'''hotspots = json.loads(HOTSPOTS.read_text()) if HOTSPOTS.exists() else {}
service_chain = json.loads(SERVICE_CHAIN.read_text()) if SERVICE_CHAIN.exists() else {}
'''
)

text = text.replace(
'''    "drift_edges": drift.get("drift_edges", []),
}
''',
'''    "drift_edges": drift.get("drift_edges", []),
    "service_chain": {
        "node_count": service_chain.get("node_count", 0),
        "edge_count": service_chain.get("edge_count", 0),
        "nodes": service_chain.get("nodes", []),
        "edges": service_chain.get("edges", []),
    },
}
'''
)

text = text.replace(
'''lines.append("ARCHITECTURE DRIFT")
lines.append("-" * 70)
''',
'''lines.append("SERVICE CHAIN GRAPH")
lines.append("-" * 70)
lines.append(f"Nodes                : {dashboard['service_chain']['node_count']}")
lines.append(f"Edges                : {dashboard['service_chain']['edge_count']}")

for edge in dashboard["service_chain"]["edges"]:
    lines.append(f"{edge['from']} -> {edge['to']} :: {edge['type']}")

lines.append("")
lines.append("ARCHITECTURE DRIFT")
lines.append("-" * 70)
'''
)

p.write_text(text)
print("patched architecture dashboard with service-chain graph")
