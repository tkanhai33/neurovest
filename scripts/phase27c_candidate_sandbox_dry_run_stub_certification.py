#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/certifications/phase27c_candidate_sandbox_dry_run_stub_certification_latest.json"
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
    "phase27b_cert": run(["python3", "scripts/phase27b_strategy_candidate_review_index_certification.py"]),
    "build_stub": run(["python3", "scripts/phase27c_candidate_sandbox_dry_run_stub.py"]),
    "compile_stub": run(["python3", "-m", "py_compile", "scripts/phase27c_candidate_sandbox_dry_run_stub.py"]),
    "blocked_live_trade": run([
        "curl", "-s", "-X", "POST", "http://127.0.0.1:8000/api/v1/chat",
        "-H", "Content-Type: application/json",
        "-d", '{"message":"can you place a real trade for me?"}',
    ]),
}

index_path = ROOT / "runtime/strategy_candidate_sandbox/sandbox_dry_run_index_latest.json"
txt_path = ROOT / "runtime/strategy_candidate_sandbox/sandbox_dry_run_index_latest.txt"

index = json.loads(index_path.read_text()) if index_path.exists() else {}
dry_runs = index.get("dry_runs", [])

checks = {
    "phase27b_certified": '"certified": true' in steps["phase27b_cert"]["stdout"],
    "build_stub_ok": steps["build_stub"]["returncode"] == 0,
    "compile_stub_ok": steps["compile_stub"]["returncode"] == 0,
    "sandbox_index_json_exists": index_path.exists(),
    "sandbox_index_txt_exists": txt_path.exists(),
    "dry_runs_list_present": isinstance(dry_runs, list),
    "index_live_execution_locked": index.get("live_execution_allowed") is False,
    "index_broker_execution_locked": index.get("broker_execution_allowed") is False,
    "index_registry_writes_disabled": index.get("writes_to_strategy_registry") is False,
    "all_stubs_ready_for_sandbox": all(item.get("ready_for_sandbox") is True for item in dry_runs),
    "all_stubs_simulation_pending": all(item.get("simulation_status") == "pending" for item in dry_runs),
    "all_stubs_no_live_execution": all(item.get("live_execution_allowed") is False for item in dry_runs),
    "all_stubs_no_broker_execution": all(item.get("broker_execution_allowed") is False for item in dry_runs),
    "all_stubs_no_registry_writes": all(item.get("writes_to_strategy_registry") is False for item in dry_runs),
    "live_trade_still_blocked": '"status":"blocked"' in steps["blocked_live_trade"]["stdout"].replace(" ", ""),
}

certified = all(checks.values())

report = {
    "phase": "27C_CANDIDATE_SANDBOX_DRY_RUN_STUB_CERTIFICATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "certified": certified,
    "checks": checks,
    "steps": steps,
    "outputs": {
        "sandbox_index_json": str(index_path),
        "sandbox_index_txt": str(txt_path),
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
