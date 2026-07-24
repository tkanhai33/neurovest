#!/usr/bin/env python3
import json
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
DOMAIN = ROOT / "runtime/repo_memory/domain_subsystem_graph_v1.json"
RUNTIME = ROOT / "runtime/repo_memory/runtime_flow_overlay_v1.json"
OUT = ROOT / "runtime/repo_memory/runtime_static_dependency_diff_v1.json"

domain = json.loads(DOMAIN.read_text())
runtime = json.loads(RUNTIME.read_text())

static_edges = set()

for edge in domain.get("edges", {}):
    src, dst = edge.split("->")
    static_edges.add((src, dst))

runtime_edges = set()

for edge in runtime.get("runtime_edges", []):
    src = edge.get("from_stack")
    dst = edge.get("to_stack")

    if not src or not dst or src == dst:
        continue

    runtime_edges.add((src, dst))

shared_edges = sorted(runtime_edges & static_edges)
runtime_only_edges = sorted(runtime_edges - static_edges)
static_only_edges = sorted(static_edges - runtime_edges)

report = {
    "phase": "10D_RUNTIME_STATIC_DEPENDENCY_DIFF",
    "generated_at": datetime.now(UTC).isoformat(),
    "static_edge_count": len(static_edges),
    "runtime_edge_count": len(runtime_edges),
    "shared_edge_count": len(shared_edges),
    "runtime_only_edge_count": len(runtime_only_edges),
    "static_only_edge_count": len(static_only_edges),
    "shared_edges": [
        {"from": a, "to": b}
        for a, b in shared_edges
    ],
    "runtime_only_edges": [
        {"from": a, "to": b}
        for a, b in runtime_only_edges
    ],
    "static_only_edges": [
        {"from": a, "to": b}
        for a, b in static_only_edges
    ],
}

OUT.write_text(json.dumps(report, indent=2))

print(json.dumps({
    "phase": report["phase"],
    "static_edge_count": report["static_edge_count"],
    "runtime_edge_count": report["runtime_edge_count"],
    "shared_edge_count": report["shared_edge_count"],
    "runtime_only_edge_count": report["runtime_only_edge_count"],
    "static_only_edge_count": report["static_only_edge_count"],
    "output": str(OUT),
}, indent=2))
