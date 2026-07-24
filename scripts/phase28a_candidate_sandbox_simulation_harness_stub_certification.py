#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/certifications/phase28a_candidate_sandbox_simulation_harness_stub_certification_latest.json"
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
    "phase27f_cert": run(["python3", "scripts/phase27f_candidate_sandbox_readiness_lock_snapshot.py"]),
    "build_harness": run(["python3", "scripts/phase28a_candidate_sandbox_simulation_harness_stub.py"]),
    "compile_harness": run(["python3", "-m", "py_compile", "scripts/phase28a_candidate_sandbox_simulation_harness_stub.py"]),
    "blocked_live_trade": run([
        "curl", "-s", "-X", "POST", "http://127.0.0.1:8000/api/v1/chat",
        "-H", "Content-Type: application/json",
        "-d", '{"message":"can you place a real trade for me?"}',
    ]),
}

harness_path = ROOT / "runtime/strategy_candidate_sandbox/simulation_harness_stub_latest.json"
txt_path = ROOT / "runtime/strategy_candidate_sandbox/simulation_harness_stub_latest.txt"

harness = json.loads(harness_path.read_text()) if harness_path.exists() else {}
items = harness.get("items", [])

checks = {
    "phase27f_certified": '"certified": true' in steps["phase27f_cert"]["stdout"],
    "build_harness_ok": steps["build_harness"]["returncode"] == 0,
    "compile_harness_ok": steps["compile_harness"]["returncode"] == 0,
    "harness_json_exists": harness_path.exists(),
    "harness_txt_exists": txt_path.exists(),
    "items_list_present": isinstance(items, list),
    "harness_stub_ready": harness.get("harness_status") == "stub_ready",
    "simulation_execute_disabled": harness.get("simulation_execute_allowed") is False,
    "historical_replay_execute_disabled": harness.get("historical_replay_execute_allowed") is False,
    "monte_carlo_execute_disabled": harness.get("monte_carlo_execute_allowed") is False,
    "live_execution_locked": harness.get("live_execution_allowed") is False,
    "broker_execution_locked": harness.get("broker_execution_allowed") is False,
    "registry_writes_disabled": harness.get("writes_to_strategy_registry") is False,
    "all_items_simulation_dry_run_only": all(item.get("simulation_mode") == "dry_run_only" for item in items),
    "all_items_simulation_execute_disabled": all(item.get("simulation_execute_allowed") is False for item in items),
    "all_items_no_live_execution": all(item.get("live_execution_allowed") is False for item in items),
    "all_items_no_broker_execution": all(item.get("broker_execution_allowed") is False for item in items),
    "all_items_no_registry_writes": all(item.get("writes_to_strategy_registry") is False for item in items),
    "live_trade_still_blocked": '"status":"blocked"' in steps["blocked_live_trade"]["stdout"].replace(" ", ""),
}

certified = all(checks.values())

report = {
    "phase": "28A_CANDIDATE_SANDBOX_SIMULATION_HARNESS_STUB_CERTIFICATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "certified": certified,
    "checks": checks,
    "steps": steps,
    "outputs": {
        "harness_json": str(harness_path),
        "harness_txt": str(txt_path),
    },
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
