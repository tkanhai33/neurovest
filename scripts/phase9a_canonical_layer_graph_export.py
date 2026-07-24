#!/usr/bin/env python3
import json
from datetime import datetime, UTC
from pathlib import Path
from collections import defaultdict

ROOT = Path(".").resolve()
INDEX = ROOT / "runtime/repo_memory/repo_index_v2.json"
DEP = ROOT / "runtime/repo_memory/dependency_graph_v1.json"
OUT = ROOT / "runtime/repo_memory/canonical_layer_graph_v1.json"

idx = json.loads(INDEX.read_text())
dep = json.loads(DEP.read_text())

files = {x["file"]: x for x in idx.get("files", [])}
layers = defaultdict(list)
edges = defaultdict(int)

for f, item in files.items():
    layers[item.get("canonical_layer", "UNCLASSIFIED")].append({
        "file": f,
        "stack": item.get("stack"),
        "component": item.get("component"),
    })

for e in dep.get("edges", []):
    a = files.get(e["from"], {}).get("canonical_layer", "UNCLASSIFIED")
    b = files.get(e["to"], {}).get("canonical_layer", "UNCLASSIFIED")
    if a != b:
        edges[f"{a}->{b}"] += 1

report = {
    "phase": "9A_CANONICAL_LAYER_GRAPH_EXPORT",
    "generated_at": datetime.now(UTC).isoformat(),
    "layer_count": len(layers),
    "cross_layer_edge_count": len(edges),
    "layers": dict(layers),
    "cross_layer_edges": dict(edges),
}

OUT.write_text(json.dumps(report, indent=2))
print(json.dumps({"phase": report["phase"], "layer_count": report["layer_count"], "cross_layer_edge_count": report["cross_layer_edge_count"], "output": str(OUT)}, indent=2))
