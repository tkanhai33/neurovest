#!/usr/bin/env python3
import json
from collections import defaultdict
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
INDEX = ROOT / "runtime/repo_memory/repo_index_v2.json"
DEP = ROOT / "runtime/repo_memory/dependency_graph_v1.json"
OUT = ROOT / "runtime/repo_memory/domain_subsystem_graph_v1.json"

idx = json.loads(INDEX.read_text())
dep = json.loads(DEP.read_text())
files = {x["file"]: x for x in idx.get("files", [])}

domain_stacks = defaultdict(list)
edges = defaultdict(int)

for file, item in files.items():
    if item.get("canonical_layer") == "L2_domain":
        domain_stacks[item.get("stack", "unknown")].append({
            "file": file,
            "component": item.get("component"),
        })

for edge in dep.get("edges", []):
    src = files.get(edge.get("from"), {})
    dst = files.get(edge.get("to"), {})
    if src.get("canonical_layer") == "L2_domain" and dst.get("canonical_layer") == "L2_domain":
        a = src.get("stack", "unknown")
        b = dst.get("stack", "unknown")
        if a != b:
            edges[f"{a}->{b}"] += 1

report = {
    "phase": "9K_DOMAIN_SUBSYSTEM_GRAPH_EXPORT",
    "generated_at": datetime.now(UTC).isoformat(),
    "subsystem_count": len(domain_stacks),
    "edge_count": len(edges),
    "subsystems": dict(domain_stacks),
    "edges": dict(edges),
}

OUT.write_text(json.dumps(report, indent=2))
print(json.dumps({
    "phase": report["phase"],
    "subsystem_count": report["subsystem_count"],
    "edge_count": report["edge_count"],
    "output": str(OUT),
}, indent=2))
