#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/certifications/phase9e_canonical_graph_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

def run(cmd):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return {"cmd": " ".join(cmd), "returncode": r.returncode, "stdout": r.stdout[-3000:], "stderr": r.stderr[-3000:]}

steps = {
    "repo_index": run(["python3", "scripts/phase4_repo_memory_indexer_v2.py"]),
    "dependency_graph": run(["python3", "scripts/phase6c_dependency_graph_export.py"]),
    "layer_export": run(["python3", "scripts/phase9a_canonical_layer_graph_export.py"]),
    "component_overlay": run(["python3", "scripts/phase9b_component_overlay_export.py"]),
    "layer_graph_png": run(["python3", "scripts/phase9c_generate_layer_colored_wire_graph.py"]),
    "component_hotspots": run(["./neuro", "repo_component_hotspots", "10"]),
    "graph_validate": run(["./neuro", "graph_validate"]),
}

files = {
    "canonical_layer_graph": ROOT / "runtime/repo_memory/canonical_layer_graph_v1.json",
    "component_overlay": ROOT / "runtime/repo_memory/component_overlay_v1.json",
    "canonical_png": ROOT / "topology_wire_graph_canonical.png",
}

layer = json.loads(files["canonical_layer_graph"].read_text()) if files["canonical_layer_graph"].exists() else {}
component = json.loads(files["component_overlay"].read_text()) if files["component_overlay"].exists() else {}

checks = {
    "all_steps_ok": all(x["returncode"] == 0 for x in steps.values()),
    "canonical_layer_graph_exists": files["canonical_layer_graph"].exists(),
    "component_overlay_exists": files["component_overlay"].exists(),
    "canonical_png_exists": files["canonical_png"].exists(),
    "canonical_png_nonempty": files["canonical_png"].exists() and files["canonical_png"].stat().st_size > 10000,
    "layer_count_ok": layer.get("layer_count", 0) >= 5,
    "component_count_ok": component.get("component_count", 0) > 0,
    "component_edge_count_ok": component.get("component_edge_count", 0) > 0,
}

certified = all(checks.values())

report = {
    "phase": "9E_CANONICAL_GRAPH_CERTIFICATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "certified": certified,
    "checks": checks,
    "steps": steps,
}

OUT.write_text(json.dumps(report, indent=2))
print(json.dumps({"phase": report["phase"], "certified": certified, "checks": checks, "output": str(OUT)}, indent=2))

if not certified:
    sys.exit(1)
