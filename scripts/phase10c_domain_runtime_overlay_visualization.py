#!/usr/bin/env python3
import json
from pathlib import Path
import matplotlib.pyplot as plt
import networkx as nx

ROOT = Path(".").resolve()
DOMAIN = ROOT / "runtime/repo_memory/domain_subsystem_graph_v1.json"
RUNTIME = ROOT / "runtime/repo_memory/runtime_flow_overlay_v1.json"
OUT = ROOT / "domain_runtime_overlay_graph.png"

domain = json.loads(DOMAIN.read_text())
runtime = json.loads(RUNTIME.read_text())

G = nx.DiGraph()

for stack, files in domain.get("subsystems", {}).items():
    G.add_node(stack, file_count=len(files), runtime=False)

runtime_stacks = set()
for edge in runtime.get("runtime_edges", []):
    src = edge.get("from_stack")
    dst = edge.get("to_stack")
    if src:
        runtime_stacks.add(src)
        if src not in G:
            G.add_node(src, file_count=0, runtime=True)
    if dst:
        runtime_stacks.add(dst)
        if dst not in G:
            G.add_node(dst, file_count=0, runtime=True)

static_edges = []
for edge, count in domain.get("edges", {}).items():
    src, dst = edge.split("->")
    G.add_edge(src, dst, static_weight=count)
    static_edges.append((src, dst))

runtime_edges = []
for edge in runtime.get("runtime_edges", []):
    src = edge.get("from_stack")
    dst = edge.get("to_stack")
    if src and dst and src != dst:
        G.add_edge(src, dst, runtime_step=edge.get("step"))
        runtime_edges.append((src, dst))

preferred_pos = {
    "chat_public": (-4.2, 2.2),
    "learning_research": (-2.6, 2.2),
    "market_data": (-3.4, 0.6),
    "strategy": (-1.8, 1.0),
    "risk": (-0.5, 0.2),
    "execution": (1.0, 0.2),
    "events": (2.4, 0.2),
    "journal_ledger": (3.8, 0.2),
    "portfolio": (2.6, -1.2),
    "core": (4.5, -1.2),
    "db_model": (-0.8, -1.5),
    "schemas": (-4.2, -1.2),
}

pos = {}
for node in G.nodes:
    if node in preferred_pos:
        pos[node] = preferred_pos[node]

remaining = [n for n in G.nodes if n not in pos]
for i, node in enumerate(remaining):
    pos[node] = (5.2, 1.5 - i * 0.8)

sizes = []
labels = {}

for node in G.nodes:
    count = G.nodes[node].get("file_count", 0)
    runtime_flag = node in runtime_stacks
    sizes.append(2200 + min(count * 220, 3200) + (800 if runtime_flag else 0))
    runtime_marker = "runtime" if runtime_flag else "static"
    labels[node] = f"{node}\nfiles={count}\n{runtime_marker}"

plt.figure(figsize=(20, 11), facecolor="#020617")
ax = plt.gca()
ax.set_facecolor("#020617")

if static_edges:
    nx.draw_networkx_edges(
        G,
        pos,
        edgelist=static_edges,
        arrowstyle="-|>",
        arrowsize=18,
        width=1.4,
        edge_color="#64748b",
        alpha=0.45,
        connectionstyle="arc3,rad=0.12",
    )

if runtime_edges:
    nx.draw_networkx_edges(
        G,
        pos,
        edgelist=runtime_edges,
        arrowstyle="-|>",
        arrowsize=26,
        width=3.4,
        edge_color="#facc15",
        alpha=0.95,
        connectionstyle="arc3,rad=0.18",
    )

node_colors = [
    "#1e293b" if node not in runtime_stacks else "#064e3b"
    for node in G.nodes
]

nx.draw_networkx_nodes(
    G,
    pos,
    node_size=sizes,
    node_color=node_colors,
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

runtime_edge_labels = {
    (edge.get("from_stack"), edge.get("to_stack")): str(edge.get("step"))
    for edge in runtime.get("runtime_edges", [])
    if edge.get("from_stack") and edge.get("to_stack") and edge.get("from_stack") != edge.get("to_stack")
}

nx.draw_networkx_edge_labels(
    G,
    pos,
    edge_labels=runtime_edge_labels,
    font_color="#facc15",
    font_size=8,
    font_family="monospace",
)

plt.title(
    "NEUROVEST DOMAIN SUBSYSTEM GRAPH | STATIC + RUNTIME FLOW OVERLAY",
    color="#34d399",
    fontsize=14,
    fontweight="bold",
    pad=20,
)

plt.text(
    -4.6,
    -2.1,
    "Yellow = runtime flow | Grey = static L2 dependency | Green nodes = runtime participants",
    color="#facc15",
    fontsize=8,
    fontfamily="monospace",
)

plt.axis("off")
plt.tight_layout()
plt.savefig(OUT, dpi=300, facecolor=plt.gcf().get_facecolor(), edgecolor="none")
plt.close()

print(json.dumps({
    "phase": "10C_DOMAIN_RUNTIME_OVERLAY_VISUALIZATION",
    "node_count": len(G.nodes),
    "static_edge_count": len(static_edges),
    "runtime_edge_count": len(runtime_edges),
    "output": str(OUT),
}, indent=2))
