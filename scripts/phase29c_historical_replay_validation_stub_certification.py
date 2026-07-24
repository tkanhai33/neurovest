#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/certifications/phase29c_historical_replay_validation_stub_certification_latest.json"
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
    "phase29b_cert": run(["python3", "scripts/phase29b_historical_replay_input_contract_certification.py"]),
    "build_validation": run(["python3", "scripts/phase29c_historical_replay_validation_stub.py"]),
    "compile_validation": run(["python3", "-m", "py_compile", "scripts/phase29c_historical_replay_validation_stub.py"]),
    "blocked_live_trade": run([
        "curl", "-s", "-X", "POST", "http://127.0.0.1:8000/api/v1/chat",
        "-H", "Content-Type: application/json",
        "-d", '{"message":"can you place a real trade for me?"}',
    ]),
}

validation_path = ROOT / "runtime/strategy_candidate_sandbox/historical_replay_validation_stub_latest.json"
txt_path = ROOT / "runtime/strategy_candidate_sandbox/historical_replay_validation_stub_latest.txt"

validation = json.loads(validation_path.read_text()) if validation_path.exists() else {}
items = validation.get("items", [])

checks = {
    "phase29b_certified": '"certified": true' in steps["phase29b_cert"]["stdout"],
    "build_validation_ok": steps["build_validation"]["returncode"] == 0,
    "compile_validation_ok": steps["compile_validation"]["returncode"] == 0,
    "validation_json_exists": validation_path.exists(),
    "validation_txt_exists": txt_path.exists(),
    "schema_id_exists": validation.get("schema_id") == "historical_replay_validation_stub_v1",
    "items_list_present": isinstance(items, list),
    "ready_for_replay_count_zero": validation.get("ready_for_replay_count") == 0,
    "historical_replay_disabled": validation.get("historical_replay_enabled") is False,
    "market_data_disabled": validation.get("market_data_enabled") is False,
    "simulation_disabled": validation.get("simulation_enabled") is False,
    "live_execution_disabled": validation.get("live_execution_enabled") is False,
    "broker_execution_disabled": validation.get("broker_execution_enabled") is False,
    "registry_write_disabled": validation.get("registry_write_enabled") is False,
    "all_items_not_ready_for_replay": all(item.get("ready_for_replay_execution") is False for item in items),
    "all_items_no_market_provider": all(item.get("market_data_provider_certified") is False for item in items),
    "all_items_no_live_execution": all(item.get("live_execution_enabled") is False for item in items),
    "all_items_no_broker_execution": all(item.get("broker_execution_enabled") is False for item in items),
    "all_items_no_registry_writes": all(item.get("registry_write_enabled") is False for item in items),
    "live_trade_still_blocked": '"status":"blocked"' in steps["blocked_live_trade"]["stdout"].replace(" ", ""),
}

certified = all(checks.values())

report = {
    "phase": "29C_HISTORICAL_REPLAY_VALIDATION_STUB_CERTIFICATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "certified": certified,
    "checks": checks,
    "steps": steps,
    "outputs": {
        "validation_json": str(validation_path),
        "validation_txt": str(txt_path),
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
