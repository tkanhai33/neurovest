#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/certifications/phase27e_candidate_sandbox_result_stub_generator_certification_latest.json"
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
    "phase27d_cert": run(["python3", "scripts/phase27d_candidate_sandbox_result_schema_certification.py"]),
    "build_results": run(["python3", "scripts/phase27e_candidate_sandbox_result_stub_generator.py"]),
    "compile_results": run(["python3", "-m", "py_compile", "scripts/phase27e_candidate_sandbox_result_stub_generator.py"]),
    "blocked_live_trade": run([
        "curl", "-s", "-X", "POST", "http://127.0.0.1:8000/api/v1/chat",
        "-H", "Content-Type: application/json",
        "-d", '{"message":"can you place a real trade for me?"}',
    ]),
}

index_path = ROOT / "runtime/strategy_candidate_sandbox/candidate_sandbox_result_stub_index_latest.json"
txt_path = ROOT / "runtime/strategy_candidate_sandbox/candidate_sandbox_result_stub_index_latest.txt"

index = json.loads(index_path.read_text()) if index_path.exists() else {}
results = index.get("results", [])

checks = {
    "phase27d_certified": '"certified": true' in steps["phase27d_cert"]["stdout"],
    "build_results_ok": steps["build_results"]["returncode"] == 0,
    "compile_results_ok": steps["compile_results"]["returncode"] == 0,
    "result_index_json_exists": index_path.exists(),
    "result_index_txt_exists": txt_path.exists(),
    "results_list_present": isinstance(results, list),
    "schema_id_present": index.get("schema_id") == "candidate_sandbox_result_v1",
    "index_simulation_pending": index.get("simulation_status") == "pending",
    "index_live_execution_locked": index.get("live_execution_allowed") is False,
    "index_broker_execution_locked": index.get("broker_execution_allowed") is False,
    "index_registry_writes_disabled": index.get("writes_to_strategy_registry") is False,
    "all_results_pending": all(item.get("simulation_status") == "pending" for item in results),
    "all_trade_counts_zero": all(item.get("trade_count") == 0 for item in results),
    "all_results_no_live_execution": all(item.get("live_execution_allowed") is False for item in results),
    "all_results_no_broker_execution": all(item.get("broker_execution_allowed") is False for item in results),
    "all_results_no_registry_writes": all(item.get("writes_to_strategy_registry") is False for item in results),
    "all_results_require_approval": all(item.get("approval_required") is True for item in results),
    "live_trade_still_blocked": '"status":"blocked"' in steps["blocked_live_trade"]["stdout"].replace(" ", ""),
}

certified = all(checks.values())

report = {
    "phase": "27E_CANDIDATE_SANDBOX_RESULT_STUB_GENERATOR_CERTIFICATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "certified": certified,
    "checks": checks,
    "steps": steps,
    "outputs": {
        "result_index_json": str(index_path),
        "result_index_txt": str(txt_path),
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
