#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()

OUT = ROOT / "runtime/certifications/phase10g_architecture_drift_dashboard_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

JSON_OUT = ROOT / "runtime/repo_memory/architecture_drift_dashboard_v1.json"
TXT_OUT = ROOT / "runtime/repo_memory/architecture_drift_dashboard_v1.txt"

def run(cmd):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return {
        "cmd": " ".join(cmd),
        "returncode": r.returncode,
        "stdout": r.stdout[-3000:],
        "stderr": r.stderr[-3000:],
    }

steps = {
    "dashboard": run(["python3", "scripts/phase10g_architecture_drift_dashboard_summary.py"]),
    "architecture_drift": run(["./neuro", "architecture_drift"]),
    "graph_validate": run(["./neuro", "graph_validate"]),
}

dashboard = json.loads(JSON_OUT.read_text()) if JSON_OUT.exists() else {}

checks = {
    "dashboard_json_exists": JSON_OUT.exists(),
    "dashboard_txt_exists": TXT_OUT.exists(),
    "dashboard_status_pass": dashboard.get("architecture_health", {}).get("status") == "PASS",
    "drift_count_zero": dashboard.get("architecture_health", {}).get("drift_count") == 0,
    "top_components_present": len(dashboard.get("top_components", [])) > 0,
    "graph_validate_ok": '"valid": true' in steps["graph_validate"]["stdout"],
    "all_steps_ok": all(x["returncode"] == 0 for x in steps.values()),
}

certified = all(checks.values())

report = {
    "phase": "10G_ARCHITECTURE_DRIFT_DASHBOARD_CERTIFICATION",
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
