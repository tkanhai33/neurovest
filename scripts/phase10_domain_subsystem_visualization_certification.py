#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/certifications/phase10_domain_subsystem_visualization_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

PNG = ROOT / "domain_subsystem_graph.png"
DOMAIN = ROOT / "runtime/repo_memory/domain_subsystem_graph_v1.json"

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
    "domain_png": run(["python3", "scripts/phase10_domain_subsystem_visualization.py"]),
}

domain = json.loads(DOMAIN.read_text()) if DOMAIN.exists() else {}

checks = {
    "all_steps_ok": all(x["returncode"] == 0 for x in steps.values()),
    "domain_export_exists": DOMAIN.exists(),
    "domain_png_exists": PNG.exists(),
    "domain_png_nonempty": PNG.exists() and PNG.stat().st_size > 10000,
    "subsystem_count_ok": domain.get("subsystem_count", 0) >= 3,
    "edge_count_ok": domain.get("edge_count", 0) >= 1,
    "strategy_present": "strategy" in domain.get("subsystems", {}),
    "portfolio_present": "portfolio" in domain.get("subsystems", {}),
    "execution_present": "execution" in domain.get("subsystems", {}),
}

certified = all(checks.values())

report = {
    "phase": "10_DOMAIN_SUBSYSTEM_VISUALIZATION_CERTIFICATION",
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
