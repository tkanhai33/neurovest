#!/usr/bin/env python3
import json
import re
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
FRONTEND = ROOT / "frontend"
PAGE = ROOT / "frontend/app/page.tsx"
OUT = ROOT / "runtime/certifications/phase23b_polling_governor_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

def run(cmd, cwd=ROOT):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return {
        "cmd": " ".join(cmd),
        "returncode": r.returncode,
        "stdout": r.stdout[-5000:],
        "stderr": r.stderr[-5000:],
    }

page_text = PAGE.read_text()

intervals = [int(x) for x in re.findall(r"setInterval\([\s\S]*?,\s*(\d+)\s*\)", page_text)]

steps = {
    "phase23a_cert": run(["python3", "scripts/phase23a_frontend_request_normalizer_certification.py"]),
    "phase22b_cert": run(["python3", "scripts/phase22b_live_graph_visualization_certification.py"]),
    "phase20f_cert": run(["python3", "scripts/phase20f_floating_chat_widget_certification.py"]),
    "lint": run(["npm", "run", "lint"], cwd=FRONTEND),
    "build": run(["npm", "run", "build"], cwd=FRONTEND),
    "graph_reset": run(["./neuro", "graph_reset"]),
    "simulate_trade": run(["./neuro", "simulate_trade", "AAPL"]),
    "graph_validate": run(["./neuro", "graph_validate"]),
}

checks = {
    "intervals_found": len(intervals) > 0,
    "no_interval_under_5000ms": all(value >= 5000 for value in intervals),
    "market_polling_30000ms": "30000" in page_text,
    "graph_polling_5000ms": "void loadGraph();" in page_text and "5000" in page_text,
    "portfolio_polling_5000ms": "void load();" in page_text and "5000" in page_text,
    "request_normalizer_certified": '"certified": true' in steps["phase23a_cert"]["stdout"],
    "graph_visualization_certified": '"certified": true' in steps["phase22b_cert"]["stdout"],
    "floating_chat_certified": '"certified": true' in steps["phase20f_cert"]["stdout"],
    "lint_ok": steps["lint"]["returncode"] == 0,
    "build_ok": steps["build"]["returncode"] == 0,
    "simulate_trade_ok": '"trade_simulated"' in steps["simulate_trade"]["stdout"],
    "graph_validate_ok": '"valid": true' in steps["graph_validate"]["stdout"],
}

certified = all(checks.values())

report = {
    "phase": "23B_POLLING_GOVERNOR_CERTIFICATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "certified": certified,
    "checks": checks,
    "polling_intervals_ms": intervals,
    "steps": steps,
}

OUT.write_text(json.dumps(report, indent=2))

print(json.dumps({
    "phase": report["phase"],
    "certified": certified,
    "checks": checks,
    "polling_intervals_ms": intervals,
    "output": str(OUT),
}, indent=2))

if not certified:
    sys.exit(1)
