#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/certifications/phase10d_runtime_static_dependency_diff_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

DIFF = ROOT / "runtime/repo_memory/runtime_static_dependency_diff_v1.json"

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
    "domain_export": run(["python3", "scripts/phase9k_domain_subsystem_graph_export.py"]),
    "runtime_overlay_export": run(["python3", "scripts/phase10c_runtime_flow_overlay_export.py"]),
    "diff_export": run(["python3", "scripts/phase10d_runtime_static_dependency_diff.py"]),
    "graph_reset": run(["./neuro", "graph_reset"]),
    "simulate_trade": run(["./neuro", "simulate_trade", "AAPL"]),
    "graph_validate": run(["./neuro", "graph_validate"]),
}

diff = json.loads(DIFF.read_text()) if DIFF.exists() else {}

checks = {
    "all_steps_ok": all(x["returncode"] == 0 for x in steps.values()),
    "diff_exists": DIFF.exists(),
    "runtime_edges_present": diff.get("runtime_edge_count", 0) > 0,
    "static_edges_present": diff.get("static_edge_count", 0) > 0,
    "runtime_only_present": diff.get("runtime_only_edge_count", 0) >= 1,
    "static_only_present": diff.get("static_only_edge_count", 0) >= 1,
    "simulate_trade_ok": '"trade_simulated"' in steps["simulate_trade"]["stdout"],
    "graph_validate_ok": '"valid": true' in steps["graph_validate"]["stdout"],
}

certified = all(checks.values())

report = {
    "phase": "10D_RUNTIME_STATIC_DEPENDENCY_DIFF_CERTIFICATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "certified": certified,
    "checks": checks,
    "diff_summary": {
        "static_edge_count": diff.get("static_edge_count"),
        "runtime_edge_count": diff.get("runtime_edge_count"),
        "shared_edge_count": diff.get("shared_edge_count"),
        "runtime_only_edge_count": diff.get("runtime_only_edge_count"),
        "static_only_edge_count": diff.get("static_only_edge_count"),
    },
    "steps": steps,
}

OUT.write_text(json.dumps(report, indent=2))

print(json.dumps({
    "phase": report["phase"],
    "certified": certified,
    "checks": checks,
    "diff_summary": report["diff_summary"],
    "output": str(OUT),
}, indent=2))

if not certified:
    sys.exit(1)
