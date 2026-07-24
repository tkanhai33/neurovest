#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
FRONTEND = ROOT / "frontend"
OUT = ROOT / "runtime/certifications/phase11e_frontend_build_type_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

def run(cmd, cwd=ROOT):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return {
        "cmd": " ".join(cmd),
        "cwd": str(cwd),
        "returncode": r.returncode,
        "stdout": r.stdout[-5000:],
        "stderr": r.stderr[-5000:],
    }

steps = {
    "frontend_exists": {
        "returncode": 0 if FRONTEND.exists() else 1,
        "stdout": str(FRONTEND),
        "stderr": "",
    },
    "npm_lint": run(["npm", "run", "lint"], cwd=FRONTEND) if FRONTEND.exists() else {"returncode": 1, "stdout": "", "stderr": "frontend missing"},
    "npm_build": run(["npm", "run", "build"], cwd=FRONTEND) if FRONTEND.exists() else {"returncode": 1, "stdout": "", "stderr": "frontend missing"},
    "api_bridge_cert": run(["python3", "scripts/phase11_live_market_price_api_bridge_certification.py"]),
    "next_proxy_cert": run(["python3", "scripts/phase11d_next_api_proxy_live_price_certification.py"]),
    "graph_reset": run(["./neuro", "graph_reset"]),
    "simulate_trade": run(["./neuro", "simulate_trade", "AAPL"]),
    "graph_validate": run(["./neuro", "graph_validate"]),
}

checks = {
    "frontend_exists": FRONTEND.exists(),
    "lint_ok": steps["npm_lint"]["returncode"] == 0,
    "build_ok": steps["npm_build"]["returncode"] == 0,
    "api_bridge_certified": '"certified": true' in steps["api_bridge_cert"]["stdout"],
    "next_proxy_certified": '"certified": true' in steps["next_proxy_cert"]["stdout"],
    "simulate_trade_ok": '"trade_simulated"' in steps["simulate_trade"]["stdout"],
    "graph_validate_ok": '"valid": true' in steps["graph_validate"]["stdout"],
}

certified = all(checks.values())

report = {
    "phase": "11E_FRONTEND_BUILD_TYPE_CERTIFICATION",
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
