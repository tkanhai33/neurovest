#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/certifications/phase9m_canonical_graph_certification_v2_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

def run(cmd):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return {
        "cmd": " ".join(cmd),
        "returncode": r.returncode,
        "stdout": r.stdout[-3000:],
        "stderr": r.stderr[-3000:],
    }

steps = {
    "repo_index": run(["python3", "scripts/phase4_repo_memory_indexer_v2.py"]),
    "dependency_graph": run(["python3", "scripts/phase6c_dependency_graph_export.py"]),
    "canonical_layer_graph": run(["python3", "scripts/phase9a_canonical_layer_graph_export.py"]),
    "component_overlay": run(["python3", "scripts/phase9b_component_overlay_export.py"]),
    "canonical_png": run(["python3", "scripts/phase9c_generate_layer_colored_wire_graph.py"]),
    "domain_subsystem": run(["python3", "scripts/phase9k_domain_subsystem_graph_export.py"]),
    "sankey_export": run(["python3", "scripts/phase9l_stack_layer_sankey_export.py"]),
    "graph_validate": run(["./neuro", "graph_validate"]),
    "repo_component_hotspots": run(["./neuro", "repo_component_hotspots", "10"]),
}

paths = {
    "repo_index": ROOT / "runtime/repo_memory/repo_index_v2.json",
    "canonical_layer_graph": ROOT / "runtime/repo_memory/canonical_layer_graph_v1.json",
    "component_overlay": ROOT / "runtime/repo_memory/component_overlay_v1.json",
    "domain_subsystem": ROOT / "runtime/repo_memory/domain_subsystem_graph_v1.json",
    "sankey": ROOT / "runtime/repo_memory/stack_layer_sankey_v1.json",
    "canonical_png": ROOT / "topology_wire_graph_canonical.png",
}

repo = json.loads(paths["repo_index"].read_text()) if paths["repo_index"].exists() else {}
canonical = json.loads(paths["canonical_layer_graph"].read_text()) if paths["canonical_layer_graph"].exists() else {}
domain = json.loads(paths["domain_subsystem"].read_text()) if paths["domain_subsystem"].exists() else {}
sankey = json.loads(paths["sankey"].read_text()) if paths["sankey"].exists() else {}

layers = set(canonical.get("layers", {}).keys())

checks = {
    "all_steps_ok": all(x["returncode"] == 0 for x in steps.values()),
    "l8_tooling_present": "L8_tooling" in layers,
    "l9_devops_present": "L9_devops" in layers,
    "l7_tests_reduced": len(canonical.get("layers", {}).get("L7_tests", [])) <= 10,
    "domain_subsystem_exists": paths["domain_subsystem"].exists(),
    "domain_subsystem_count_ok": domain.get("subsystem_count", 0) >= 3,
    "sankey_exists": paths["sankey"].exists(),
    "sankey_links_ok": sankey.get("link_count", 0) > 0,
    "canonical_png_exists": paths["canonical_png"].exists(),
    "canonical_png_nonempty": paths["canonical_png"].exists() and paths["canonical_png"].stat().st_size > 10000,
    "repo_has_canonical_layers": all("canonical_layer" in x for x in repo.get("files", [])),
}

certified = all(checks.values())

report = {
    "phase": "9M_CANONICAL_GRAPH_CERTIFICATION_V2",
    "generated_at": datetime.now(UTC).isoformat(),
    "certified": certified,
    "checks": checks,
    "layer_counts": {
        layer: len(files)
        for layer, files in canonical.get("layers", {}).items()
    },
    "steps": steps,
}

OUT.write_text(json.dumps(report, indent=2))
print(json.dumps({
    "phase": report["phase"],
    "certified": certified,
    "checks": checks,
    "layer_counts": report["layer_counts"],
    "output": str(OUT),
}, indent=2))

if not certified:
    sys.exit(1)
