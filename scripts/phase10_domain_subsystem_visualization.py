#!/usr/bin/env python3
import json
from pathlib import Path
import matplotlib.pyplot as plt
import networkx as nx

ROOT = Path(".").resolve()
DOMAIN = ROOT / "runtime/repo_memory/domain_subsystem_graph_v1.json"
OUT = ROOT / "domain_subsystem_graph.png"

data = json.loads(DOMAIN.read_text())

G = nx.DiGraph()

for stack, files in data.get("subsystems", {}).items():
    G.add_node(stack, file_count=len(files))

for edge, count in data.get("edges", {}).items():
    src, dst = edge.split("->")
    G.add_edge(src, dst, weight=count)

preferred_pos = {
    "market_data": (-3.0, 0.8),
    "strategy": (-1.5, 1.4),
    "risk": (-1.5, -0.2),
    "portfolio": (0.4, 0.8),
    "execution": (2.3, 0.4),
    "learning_research": (-0.2, 2.3),
    "db_model": (0.5, -1.0),
    "schemas": (-3.0, -0.7),
}

pos = {}
for node in G.nodes:
    if node in preferred_pos:
        pos[node] = preferred_pos[node]

remaining = [n for n in G.nodes if n not in pos]
for i, node in enumerate(remaining):
    pos[node] = (3.5, i * 0.8)

sizes = []
labels = {}

for node in G.nodes:
    count = G.nodes[node].get("file_count", 1)
    sizes.append(2200 + min(count * 220, 3200))
    labels[node] = f"{node}\nfiles={count}"

edge_widths = [
    1.8 + min(G.edges[e].get("weight", 1) * 0.8, 4.0)
    for e in G.edges
]

plt.figure(figsize=(18, 10), facecolor="#020617")
ax = plt.gca()
ax.set_facecolor("#020617")

nx.draw_networkx_edges(
    G,
    pos,
    arrowstyle="-|>",
    arrowsize=24,
    width=edge_widths,
    edge_color="#facc15",
    connectionstyle="arc3,rad=0.16",
)

nx.draw_networkx_nodes(
    G,
    pos,
    node_size=sizes,
    node_color="#1e293b",
    edgecolors="#38bdf8",
    linewidths=2.8,
)

nx.draw_networkx_labels(
    G,
    pos,
    labels=labels,
    font_size=8,
    font_color="#f8fafc",
    font_weight="bold",
    font_family="monospace",
)

plt.title(
    "NEUROVEST L2 DOMAIN SUBSYSTEM GRAPH",
    color="#34d399",
    fontsize=15,
    fontweight="bold",
    pad=20,
)

plt.text(
    -3.5,
    -1.7,
    "Node size = files in subsystem | Yellow arrows = L2 domain dependencies",
    color="#facc15",
    fontsize=8,
    fontfamily="monospace",
)

plt.axis("off")
plt.tight_layout()
plt.savefig(OUT, dpi=300, facecolor=plt.gcf().get_facecolor(), edgecolor="none")
plt.close()

print(json.dumps({
    "phase": "10_DOMAIN_SUBSYSTEM_VISUALIZATION",
    "node_count": len(G.nodes),
    "edge_count": len(G.edges),
    "output": str(OUT),
}, indent=2))
