#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/certifications/phase12g_service_chain_dashboard_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

DASH_JSON = ROOT / "runtime/repo_memory/architecture_drift_dashboard_v1.json"
DASH_TXT = ROOT / "runtime/repo_memory/architecture_drift_dashboard_v1.txt"

def run(cmd):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return {
        "cmd": " ".join(cmd),
        "returncode": r.returncode,
        "stdout": r.stdout[-5000:],
        "stderr": r.stderr[-5000:],
    }

steps = {
    "patch": run(["python3", "scripts/phase12g_add_service_chain_to_dashboard.py"]),
    "service_chain_cert": run(["python3", "scripts/phase12f_service_chain_certification.py"]),
    "dashboard_refresh": run(["python3", "scripts/phase10g_architecture_drift_dashboard_summary.py"]),
    "architecture_dashboard": run(["./neuro", "architecture_dashboard"]),
    "architecture_drift": run(["./neuro", "architecture_drift"]),
    "graph_reset": run(["./neuro", "graph_reset"]),
    "simulate_trade": run(["./neuro", "simulate_trade", "AAPL"]),
    "graph_validate": run(["./neuro", "graph_validate"]),
}

dash = json.loads(DASH_JSON.read_text()) if DASH_JSON.exists() else {}
dash_text = DASH_TXT.read_text() if DASH_TXT.exists() else ""

service_chain = dash.get("service_chain", {})

checks = {
    "patch_ok": steps["patch"]["returncode"] == 0,
    "service_chain_certified": '"certified": true' in steps["service_chain_cert"]["stdout"],
    "dashboard_refresh_ok": steps["dashboard_refresh"]["returncode"] == 0,
    "dashboard_json_exists": DASH_JSON.exists(),
    "dashboard_txt_exists": DASH_TXT.exists(),
    "dashboard_has_service_chain": "service_chain" in dash,
    "service_chain_node_count_ok": service_chain.get("node_count") == 6,
    "service_chain_edge_count_ok": service_chain.get("edge_count") == 5,
    "dashboard_txt_has_service_chain": "SERVICE CHAIN GRAPH" in dash_text,
    "architecture_drift_pass": '"status": "pass"' in steps["architecture_drift"]["stdout"],
    "simulate_trade_ok": '"trade_simulated"' in steps["simulate_trade"]["stdout"],
    "graph_validate_ok": '"valid": true' in steps["graph_validate"]["stdout"],
}

certified = all(checks.values())

report = {
    "phase": "12G_SERVICE_CHAIN_DASHBOARD_CERTIFICATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "certified": certified,
    "checks": checks,
    "service_chain": service_chain,
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
