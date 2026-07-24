#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/certifications/phase10h_architecture_dashboard_command_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)


def run(cmd):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return {
        "cmd": " ".join(cmd),
        "returncode": r.returncode,
        "stdout": r.stdout[-5000:],
        "stderr": r.stderr[-3000:],
    }


def payload(step):
    text = step.get("stdout", "").strip()

    try:
        return json.loads(text)
    except Exception:
        pass

    # Find the first full JSON object in noisy stdout using brace depth.
    start = text.find("{")
    while start != -1:
        depth = 0
        for i in range(start, len(text)):
            ch = text[i]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    candidate = text[start:i + 1]
                    try:
                        return json.loads(candidate)
                    except Exception:
                        break
        start = text.find("{", start + 1)

    return {}


steps = {
    "dashboard_refresh": run(["python3", "scripts/phase10g_architecture_drift_dashboard_summary.py"]),
    "architecture_dashboard": run(["./neuro", "architecture_dashboard"]),
    "architecture_drift": run(["./neuro", "architecture_drift"]),
    "graph_reset": run(["./neuro", "graph_reset"]),
    "simulate_trade": run(["./neuro", "simulate_trade", "AAPL"]),
    "graph_validate": run(["./neuro", "graph_validate"]),
}

dashboard_file = ROOT / "runtime/repo_memory/architecture_drift_dashboard_v1.json"
dash = json.loads(dashboard_file.read_text()) if dashboard_file.exists() else {}
drift = payload(steps["architecture_drift"]).get("response", {}).get("data", {})

checks = {
    "all_steps_ok": all(x["returncode"] == 0 for x in steps.values()),
    "dashboard_found": bool(dash),
    "dashboard_status_pass": dash.get("architecture_health", {}).get("status") == "PASS",
    "dashboard_drift_zero": dash.get("architecture_health", {}).get("drift_count") == 0,
    "dashboard_text_present": (ROOT / "runtime/repo_memory/architecture_drift_dashboard_v1.txt").exists(),
    "drift_command_pass": drift.get("status") == "pass",
    "simulate_trade_ok": '"trade_simulated"' in steps["simulate_trade"]["stdout"],
    "graph_validate_ok": '"valid": true' in steps["graph_validate"]["stdout"],
}

certified = all(checks.values())

report = {
    "phase": "10H_ARCHITECTURE_DASHBOARD_COMMAND_CERTIFICATION",
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
