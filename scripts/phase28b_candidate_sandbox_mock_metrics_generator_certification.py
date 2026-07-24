#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/certifications/phase28b_candidate_sandbox_mock_metrics_generator_certification_latest.json"
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
    "phase28a_cert": run(["python3", "scripts/phase28a_candidate_sandbox_simulation_harness_stub_certification.py"]),
    "build_mock_metrics": run(["python3", "scripts/phase28b_candidate_sandbox_mock_metrics_generator.py"]),
    "compile_mock_metrics": run(["python3", "-m", "py_compile", "scripts/phase28b_candidate_sandbox_mock_metrics_generator.py"]),
    "blocked_live_trade": run([
        "curl", "-s", "-X", "POST", "http://127.0.0.1:8000/api/v1/chat",
        "-H", "Content-Type: application/json",
        "-d", '{"message":"can you place a real trade for me?"}',
    ]),
}

index_path = ROOT / "runtime/strategy_candidate_sandbox/candidate_sandbox_mock_metrics_index_latest.json"
txt_path = ROOT / "runtime/strategy_candidate_sandbox/candidate_sandbox_mock_metrics_index_latest.txt"

index = json.loads(index_path.read_text()) if index_path.exists() else {}
results = index.get("results", [])

checks = {
    "phase28a_certified": '"certified": true' in steps["phase28a_cert"]["stdout"],
    "build_mock_metrics_ok": steps["build_mock_metrics"]["returncode"] == 0,
    "compile_mock_metrics_ok": steps["compile_mock_metrics"]["returncode"] == 0,
    "mock_index_json_exists": index_path.exists(),
    "mock_index_txt_exists": txt_path.exists(),
    "results_list_present": isinstance(results, list),
    "index_mock_only": index.get("mock_only") is True,
    "index_no_market_data": index.get("market_data_used") is False,
    "index_no_backtest": index.get("backtest_executed") is False,
    "index_no_simulation": index.get("simulation_executed") is False,
    "index_no_promotion": index.get("promotion_allowed") is False,
    "index_live_execution_locked": index.get("live_execution_allowed") is False,
    "index_broker_execution_locked": index.get("broker_execution_allowed") is False,
    "index_registry_writes_disabled": index.get("writes_to_strategy_registry") is False,
    "all_results_mock_only": all(item.get("mock_only") is True for item in results),
    "all_results_no_market_data": all(item.get("market_data_used") is False for item in results),
    "all_results_no_backtest": all(item.get("backtest_executed") is False for item in results),
    "all_results_no_simulation": all(item.get("simulation_executed") is False for item in results),
    "all_results_trade_count_zero": all(item.get("trade_count") == 0 for item in results),
    "all_results_no_live_execution": all(item.get("live_execution_allowed") is False for item in results),
    "all_results_no_broker_execution": all(item.get("broker_execution_allowed") is False for item in results),
    "all_results_no_registry_writes": all(item.get("writes_to_strategy_registry") is False for item in results),
    "live_trade_still_blocked": '"status":"blocked"' in steps["blocked_live_trade"]["stdout"].replace(" ", ""),
}

certified = all(checks.values())

report = {
    "phase": "28B_CANDIDATE_SANDBOX_MOCK_METRICS_GENERATOR_CERTIFICATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "certified": certified,
    "checks": checks,
    "steps": steps,
    "outputs": {
        "mock_metrics_index_json": str(index_path),
        "mock_metrics_index_txt": str(txt_path),
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
