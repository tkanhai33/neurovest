#!/usr/bin/env python3
import json
from datetime import datetime, UTC
from pathlib import Path
from collections import defaultdict

ROOT = Path(".").resolve()
INDEX = ROOT / "runtime/repo_memory/repo_index_v2.json"
DEP = ROOT / "runtime/repo_memory/dependency_graph_v1.json"
OUT = ROOT / "runtime/repo_memory/component_overlay_v1.json"

idx = json.loads(INDEX.read_text())
dep = json.loads(DEP.read_text())
files = {x["file"]: x for x in idx.get("files", [])}

component_edges = defaultdict(int)
components = defaultdict(lambda: {"files": [], "in_degree": 0, "out_degree": 0})

for f, item in files.items():
    c = item.get("component", Path(f).stem)
    components[c]["files"].append(f)
    components[c]["stack"] = item.get("stack")
    components[c]["canonical_layer"] = item.get("canonical_layer")

for e in dep.get("edges", []):
    src = files.get(e["from"], {})
    dst = files.get(e["to"], {})
    a = src.get("component")
    b = dst.get("component")
    if not a or not b or a == b:
        continue
    component_edges[f"{a}->{b}"] += 1
    components[a]["out_degree"] += 1
    components[b]["in_degree"] += 1

report = {
    "phase": "9B_COMPONENT_OVERLAY_EXPORT",
    "generated_at": datetime.now(UTC).isoformat(),
    "component_count": len(components),
    "component_edge_count": len(component_edges),
    "components": dict(components),
    "component_edges": dict(component_edges),
}

OUT.write_text(json.dumps(report, indent=2))
print(json.dumps({"phase": report["phase"], "component_count": report["component_count"], "component_edge_count": report["component_edge_count"], "output": str(OUT)}, indent=2))
