#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/certifications/phase10c_runtime_flow_overlay_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

RUNTIME = ROOT / "runtime/repo_memory/runtime_flow_overlay_v1.json"
PNG = ROOT / "domain_runtime_overlay_graph.png"

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
    "runtime_overlay_png": run(["python3", "scripts/phase10c_domain_runtime_overlay_visualization.py"]),
    "graph_reset": run(["./neuro", "graph_reset"]),
    "simulate_trade": run(["./neuro", "simulate_trade", "AAPL"]),
    "graph_validate": run(["./neuro", "graph_validate"]),
}

runtime = json.loads(RUNTIME.read_text()) if RUNTIME.exists() else {}

checks = {
    "all_steps_ok": all(x["returncode"] == 0 for x in steps.values()),
    "runtime_overlay_exists": RUNTIME.exists(),
    "runtime_step_count_ok": runtime.get("runtime_step_count") == 11,
    "png_exists": PNG.exists(),
    "png_nonempty": PNG.exists() and PNG.stat().st_size > 10000,
    "simulate_trade_ok": '"trade_simulated"' in steps["simulate_trade"]["stdout"],
    "graph_validate_ok": '"valid": true' in steps["graph_validate"]["stdout"],
}

certified = all(checks.values())

report = {
    "phase": "10C_RUNTIME_FLOW_OVERLAY_CERTIFICATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "certified": certified,
    "checks": checks,
    "steps": steps,
}

OUT.write_text(json.dumps(report, indent=2))

print(json.dumps({
    "phase": report["phase"],
    "certified": certified,
    "checks": checks,
    "output": str(OUT),
}, indent=2))

if not certified:
    sys.exit(1)
