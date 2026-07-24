#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
FRONTEND = ROOT / "frontend"
OUT = ROOT / "runtime/certifications/phase22_live_graph_tab_certification_latest.json"
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
    "patch": run(["python3", "scripts/phase22_live_graph_tab.py"]),
    "lint": run(["npm", "run", "lint"], cwd=FRONTEND),
    "build": run(["npm", "run", "build"], cwd=FRONTEND),
    "graph_reset": run(["./neuro", "graph_reset"]),
    "simulate_trade": run(["./neuro", "simulate_trade", "AAPL"]),
    "graph_validate": run(["./neuro", "graph_validate"]),
}

service = ROOT / "frontend/services/graphService.ts"
route = ROOT / "frontend/app/api/v1/graph/live/route.ts"
page = ROOT / "frontend/app/page.tsx"

service_text = service.read_text() if service.exists() else ""
route_text = route.read_text() if route.exists() else ""
page_text = page.read_text() if page.exists() else ""

checks = {
    "patch_ok": steps["patch"]["returncode"] == 0,
    "graph_service_exists": service.exists(),
    "graph_service_has_getLiveGraph": "getLiveGraph" in service_text,
    "next_graph_proxy_exists": route.exists(),
    "next_graph_proxy_uses_backend": "http://127.0.0.1:8000/api/v1/graph/live" in route_text,
    "graph_panel_exists": "function LiveSystemGraphPanel()" in page_text,
    "graph_panel_rendered": "<LiveSystemGraphPanel />" in page_text,
    "lint_ok": steps["lint"]["returncode"] == 0,
    "build_ok": steps["build"]["returncode"] == 0,
    "simulate_trade_ok": '"trade_simulated"' in steps["simulate_trade"]["stdout"],
    "graph_validate_ok": '"valid": true' in steps["graph_validate"]["stdout"],
}

certified = all(checks.values())

report = {
    "phase": "22_LIVE_GRAPH_TAB_CERTIFICATION",
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
