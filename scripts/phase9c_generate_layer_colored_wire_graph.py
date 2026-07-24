#!/usr/bin/env python3
import json
from pathlib import Path
import matplotlib.pyplot as plt
import networkx as nx

ROOT = Path(".").resolve()
LAYER = ROOT / "runtime/repo_memory/canonical_layer_graph_v1.json"
OUT = ROOT / "topology_wire_graph_canonical.png"

data = json.loads(LAYER.read_text())
G = nx.DiGraph()

layer_order = [
    "L0_external_adapter",
    "L1_security_auth_safety",
    "L2_domain",
    "L3_service_facade",
    "L4_runtime_orchestration",
    "L5_api_presentation",
    "L6_frontend",
    "L7_tests",
]

for layer in data.get("layers", {}):
    G.add_node(layer)

for edge, count in data.get("cross_layer_edges", {}).items():
    a, b = edge.split("->")
    G.add_edge(a, b, weight=count)

pos = {}
for i, layer in enumerate(layer_order):
    if layer in G.nodes:
        pos[layer] = (i * 2.2, 0)

for node in G.nodes:
    if node not in pos:
        pos[node] = (len(pos) * 2.2, -1.5)

sizes = []
labels = {}
for node in G.nodes:
    file_count = len(data.get("layers", {}).get(node, []))
    sizes.append(2500 + min(file_count * 90, 3000))
    labels[node] = f"{node}\nfiles={file_count}"

plt.figure(figsize=(22, 8), facecolor="#020617")
ax = plt.gca()
ax.set_facecolor("#020617")

nx.draw_networkx_edges(G, pos, arrowstyle="-|>", arrowsize=22, width=2.2, edge_color="#facc15", connectionstyle="arc3,rad=0.12")
nx.draw_networkx_nodes(G, pos, node_size=sizes, node_color="#1e293b", edgecolors="#38bdf8", linewidths=2.5)
nx.draw_networkx_labels(G, pos, labels=labels, font_size=8, font_color="#f8fafc", font_weight="bold", font_family="monospace")

plt.title("NEUROVEST CANONICAL LAYER GRAPH | V3 TOPOLOGY", color="#34d399", fontsize=14, fontweight="bold", pad=20)
plt.axis("off")
plt.tight_layout()
plt.savefig(OUT, dpi=300, facecolor=plt.gcf().get_facecolor(), edgecolor="none")
plt.close()

print(json.dumps({"phase": "9C_LAYER_COLORED_WIRE_GRAPH", "output": str(OUT), "node_count": len(G.nodes), "edge_count": len(G.edges)}, indent=2))
