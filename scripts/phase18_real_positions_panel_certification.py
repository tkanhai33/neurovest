#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
FRONTEND = ROOT / "frontend"
PAGE = ROOT / "frontend/app/page.tsx"

OUT = ROOT / "runtime/certifications/phase18_real_positions_panel_certification_latest.json"
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
    "patch": run(["python3", "scripts/phase18_real_positions_panel_component.py"]),
    "route_map_cert": run(["python3", "scripts/phase17_dashboard_route_map_certification.py"]),
    "lint": run(["npm", "run", "lint"], cwd=FRONTEND),
    "build": run(["npm", "run", "build"], cwd=FRONTEND),
    "graph_reset": run(["./neuro", "graph_reset"]),
    "simulate_trade": run(["./neuro", "simulate_trade", "AAPL"]),
    "graph_validate": run(["./neuro", "graph_validate"]),
}

page_text = PAGE.read_text() if PAGE.exists() else ""

checks = {
    "positions_panel_component_exists":
        "function PositionsPanel({" in page_text,
    "positions_panel_rendered":
        "<PositionsPanel positions={positions} />" in page_text,
    "route_map_certified":
        '"certified": true' in steps["route_map_cert"]["stdout"],
    "lint_ok":
        steps["lint"]["returncode"] == 0,
    "build_ok":
        steps["build"]["returncode"] == 0,
    "simulate_trade_ok":
        '"trade_simulated"' in steps["simulate_trade"]["stdout"],
    "graph_validate_ok":
        '"valid": true' in steps["graph_validate"]["stdout"],
}

certified = all(checks.values())

report = {
    "phase": "18_REAL_POSITIONS_PANEL_CERTIFICATION",
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
