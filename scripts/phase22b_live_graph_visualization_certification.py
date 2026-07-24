#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
FRONTEND = ROOT / "frontend"
PAGE = ROOT / "frontend/app/page.tsx"
OUT = ROOT / "runtime/certifications/phase22b_live_graph_visualization_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

def run(cmd, cwd=ROOT):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return {
        "cmd": " ".join(cmd),
        "returncode": r.returncode,
        "stdout": r.stdout[-5000:],
        "stderr": r.stderr[-5000:],
    }

steps = {
    "patch": run(["python3", "scripts/phase22b_live_graph_visualization.py"]),
    "phase22_cert": run(["python3", "scripts/phase22_live_graph_tab_certification.py"]),
    "lint": run(["npm", "run", "lint"], cwd=FRONTEND),
    "build": run(["npm", "run", "build"], cwd=FRONTEND),
    "graph_reset": run(["./neuro", "graph_reset"]),
    "simulate_trade": run(["./neuro", "simulate_trade", "AAPL"]),
    "graph_validate": run(["./neuro", "graph_validate"]),
}

page_text = PAGE.read_text() if PAGE.exists() else ""

checks = {
    "patch_ok": steps["patch"]["returncode"] == 0,
    "graph_panel_exists": "function LiveSystemGraphPanel()" in page_text,
    "runtime_flow_title_exists": "Runtime Flow" in page_text,
    "node_pulse_exists": "bg-emerald-300" in page_text,
    "edge_arrow_exists": "rotate-45" in page_text,
    "active_edges_section_exists": "Active Edges" in page_text,
    "event_count_rendered": "node.event_count" in page_text,
    "symbol_rendered": "node.symbol" in page_text,
    "phase22_certified": '"certified": true' in steps["phase22_cert"]["stdout"],
    "lint_ok": steps["lint"]["returncode"] == 0,
    "build_ok": steps["build"]["returncode"] == 0,
    "simulate_trade_ok": '"trade_simulated"' in steps["simulate_trade"]["stdout"],
    "graph_validate_ok": '"valid": true' in steps["graph_validate"]["stdout"],
}

certified = all(checks.values())

report = {
    "phase": "22B_LIVE_GRAPH_VISUALIZATION_CERTIFICATION",
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
