#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/certifications/phase10e_diff_classification_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

CLASSIFIED = ROOT / "runtime/repo_memory/runtime_static_diff_classification_v1.json"

def run(cmd):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return {
        "cmd": " ".join(cmd),
        "returncode": r.returncode,
        "stdout": r.stdout[-3000:],
        "stderr": r.stderr[-3000:],
    }

steps = {
    "runtime_static_diff": run(["python3", "scripts/phase10d_runtime_static_dependency_diff.py"]),
    "diff_classification": run(["python3", "scripts/phase10e_classify_runtime_static_diff_edges.py"]),
    "graph_reset": run(["./neuro", "graph_reset"]),
    "simulate_trade": run(["./neuro", "simulate_trade", "AAPL"]),
    "graph_validate": run(["./neuro", "graph_validate"]),
}

classified = json.loads(CLASSIFIED.read_text()) if CLASSIFIED.exists() else {}

checks = {
    "all_steps_ok": all(x["returncode"] == 0 for x in steps.values()),
    "classification_exists": CLASSIFIED.exists(),
    "runtime_only_classified": classified.get("runtime_only_count", 0) >= 1,
    "static_only_classified": classified.get("static_only_count", 0) >= 1,
    "no_unclassified_drift": classified.get("drift_count") == 0,
    "simulate_trade_ok": '"trade_simulated"' in steps["simulate_trade"]["stdout"],
    "graph_validate_ok": '"valid": true' in steps["graph_validate"]["stdout"],
}

certified = all(checks.values())

report = {
    "phase": "10E_DIFF_CLASSIFICATION_CERTIFICATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "certified": certified,
    "checks": checks,
    "classification_summary": {
        "runtime_only_count": classified.get("runtime_only_count"),
        "static_only_count": classified.get("static_only_count"),
        "shared_count": classified.get("shared_count"),
        "drift_count": classified.get("drift_count"),
    },
    "steps": steps,
}

OUT.write_text(json.dumps(report, indent=2))

print(json.dumps({
    "phase": report["phase"],
    "certified": certified,
    "checks": checks,
    "classification_summary": report["classification_summary"],
    "output": str(OUT),
}, indent=2))

if not certified:
    sys.exit(1)
