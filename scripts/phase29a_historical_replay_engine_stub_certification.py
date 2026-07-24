#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/certifications/phase29a_historical_replay_engine_stub_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

def run(cmd, cwd=ROOT):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return {"cmd": " ".join(cmd), "returncode": r.returncode, "stdout": r.stdout[-5000:], "stderr": r.stderr[-5000:]}

steps = {
    "phase28d_cert": run(["python3", "scripts/phase28d_candidate_sandbox_execution_contract_certification.py"]),
    "build_stub": run(["python3", "scripts/phase29a_historical_replay_engine_stub.py"]),
    "compile_stub": run(["python3", "-m", "py_compile", "scripts/phase29a_historical_replay_engine_stub.py"]),
    "blocked_live_trade": run([
        "curl", "-s", "-X", "POST", "http://127.0.0.1:8000/api/v1/chat",
        "-H", "Content-Type: application/json",
        "-d", '{"message":"can you place a real trade for me?"}',
    ]),
}

stub_path = ROOT / "runtime/strategy_candidate_sandbox/historical_replay_engine_stub_latest.json"
txt_path = ROOT / "runtime/strategy_candidate_sandbox/historical_replay_engine_stub_latest.txt"

stub = json.loads(stub_path.read_text()) if stub_path.exists() else {}

checks = {
    "phase28d_certified": '"certified": true' in steps["phase28d_cert"]["stdout"],
    "build_stub_ok": steps["build_stub"]["returncode"] == 0,
    "compile_stub_ok": steps["compile_stub"]["returncode"] == 0,
    "stub_json_exists": stub_path.exists(),
    "stub_txt_exists": txt_path.exists(),
    "engine_status_stub_only": stub.get("engine_status") == "stub_only",
    "historical_replay_disabled": stub.get("historical_replay_enabled") is False,
    "historical_replay_execute_disabled": stub.get("historical_replay_execute_allowed") is False,
    "market_data_disabled": stub.get("market_data_enabled") is False,
    "simulation_disabled": stub.get("simulation_enabled") is False,
    "monte_carlo_disabled": stub.get("monte_carlo_enabled") is False,
    "promotion_disabled": stub.get("promotion_enabled") is False,
    "live_execution_disabled": stub.get("live_execution_enabled") is False,
    "broker_execution_disabled": stub.get("broker_execution_enabled") is False,
    "registry_write_disabled": stub.get("registry_write_enabled") is False,
    "expected_trade_count_zero": stub.get("expected_outputs", {}).get("trade_count") == 0,
    "live_trade_still_blocked": '"status":"blocked"' in steps["blocked_live_trade"]["stdout"].replace(" ", ""),
}

certified = all(checks.values())

report = {
    "phase": "29A_HISTORICAL_REPLAY_ENGINE_STUB_CERTIFICATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "certified": certified,
    "checks": checks,
    "steps": steps,
    "outputs": {
        "stub_json": str(stub_path),
        "stub_txt": str(txt_path),
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
