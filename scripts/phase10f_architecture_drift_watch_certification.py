#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/certifications/phase10f_architecture_drift_watch_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

def run(cmd):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return {
        "cmd": " ".join(cmd),
        "returncode": r.returncode,
        "stdout": r.stdout[-3000:],
        "stderr": r.stderr[-3000:],
    }

def payload(step):
    text = step.get("stdout", "").strip()

    # Prefer parsing full stdout first.
    try:
        return json.loads(text)
    except Exception:
        pass

    # Fall back to the last valid JSON object in noisy stdout.
    lines = text.splitlines()
    for i in range(len(lines)):
        candidate = "\n".join(lines[i:]).strip()
        if not candidate.startswith("{"):
            continue
        try:
            return json.loads(candidate)
        except Exception:
            continue

    return {}

steps = {
    "diff": run(["python3", "scripts/phase10d_runtime_static_dependency_diff.py"]),
    "classify": run(["python3", "scripts/phase10e_classify_runtime_static_diff_edges.py"]),
    "architecture_drift": run(["./neuro", "architecture_drift"]),
    "graph_reset": run(["./neuro", "graph_reset"]),
    "simulate_trade": run(["./neuro", "simulate_trade", "AAPL"]),
    "graph_validate": run(["./neuro", "graph_validate"]),
}

drift = payload(steps["architecture_drift"]).get("response", {}).get("data", {})

checks = {
    "all_steps_ok": all(x["returncode"] == 0 for x in steps.values()),
    "drift_command_ok": drift.get("status") == "pass",
    "drift_count_zero": drift.get("drift_count") == 0,
    "runtime_only_present": drift.get("runtime_only_count", 0) >= 1,
    "static_only_present": drift.get("static_only_count", 0) >= 1,
    "simulate_trade_ok": '"trade_simulated"' in steps["simulate_trade"]["stdout"],
    "graph_validate_ok": '"valid": true' in steps["graph_validate"]["stdout"],
}

certified = all(checks.values())

report = {
    "phase": "10F_ARCHITECTURE_DRIFT_WATCH_CERTIFICATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "certified": certified,
    "checks": checks,
    "drift": drift,
    "steps": steps,
}

OUT.write_text(json.dumps(report, indent=2))

print(json.dumps({
    "phase": report["phase"],
    "certified": certified,
    "checks": checks,
    "drift": drift,
    "output": str(OUT),
}, indent=2))

if not certified:
    sys.exit(1)
