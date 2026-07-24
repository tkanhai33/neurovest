#!/usr/bin/env python3
import json
from collections import defaultdict
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
INDEX = ROOT / "runtime/repo_memory/repo_index_v2.json"
OUT = ROOT / "runtime/repo_memory/stack_layer_sankey_v1.json"

idx = json.loads(INDEX.read_text())
flows = defaultdict(int)

for item in idx.get("files", []):
    stack = item.get("stack", "unknown")
    layer = item.get("canonical_layer", "unknown")
    flows[(stack, layer)] += 1

nodes = sorted(set([x for pair in flows for x in pair]))
links = [
    {
        "source": stack,
        "target": layer,
        "value": count,
    }
    for (stack, layer), count in sorted(flows.items())
]

report = {
    "phase": "9L_STACK_LAYER_SANKEY_EXPORT",
    "generated_at": datetime.now(UTC).isoformat(),
    "node_count": len(nodes),
    "link_count": len(links),
    "nodes": nodes,
    "links": links,
}

OUT.write_text(json.dumps(report, indent=2))
print(json.dumps({
    "phase": report["phase"],
    "node_count": report["node_count"],
    "link_count": report["link_count"],
    "output": str(OUT),
}, indent=2))
