#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/certifications/phase29e_historical_replay_market_data_provider_contract_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

def run(cmd, cwd=ROOT):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return {"cmd": " ".join(cmd), "returncode": r.returncode, "stdout": r.stdout[-5000:], "stderr": r.stderr[-5000:]}

steps = {
    "phase29d_cert": run(["python3", "scripts/phase29d_historical_replay_readiness_snapshot.py"]),
    "build_contract": run(["python3", "scripts/phase29e_historical_replay_market_data_provider_contract.py"]),
    "compile_contract": run(["python3", "-m", "py_compile", "scripts/phase29e_historical_replay_market_data_provider_contract.py"]),
    "blocked_live_trade": run([
        "curl", "-s", "-X", "POST", "http://127.0.0.1:8000/api/v1/chat",
        "-H", "Content-Type: application/json",
        "-d", '{"message":"can you place a real trade for me?"}',
    ]),
}

contract_path = ROOT / "runtime/strategy_candidate_sandbox/historical_replay_market_data_provider_contract_v1.json"
txt_path = ROOT / "runtime/strategy_candidate_sandbox/historical_replay_market_data_provider_contract_v1.txt"

contract = json.loads(contract_path.read_text()) if contract_path.exists() else {}
provider = contract.get("provider_contract", {})
flags = contract.get("execution_flags", {})
output_shape = provider.get("required_output_shape", {})

checks = {
    "phase29d_certified": '"certified": true' in steps["phase29d_cert"]["stdout"],
    "build_contract_ok": steps["build_contract"]["returncode"] == 0,
    "compile_contract_ok": steps["compile_contract"]["returncode"] == 0,
    "contract_json_exists": contract_path.exists(),
    "contract_txt_exists": txt_path.exists(),
    "schema_id_exists": contract.get("schema_id") == "historical_replay_market_data_provider_contract_v1",
    "provider_name_not_wired": provider.get("provider_name") == "not_wired",
    "required_function_exists": provider.get("required_function") == "get_historical_bars",
    "required_symbol_input": "symbol" in provider.get("required_inputs", {}),
    "required_start_date_input": "start_date" in provider.get("required_inputs", {}),
    "required_end_date_input": "end_date" in provider.get("required_inputs", {}),
    "required_interval_input": "interval" in provider.get("required_inputs", {}),
    "required_output_has_bars": "bars" in output_shape,
    "required_output_has_bar_count": "bar_count" in output_shape,
    "provider_not_wired": flags.get("provider_wired") is False,
    "market_data_disabled": flags.get("market_data_enabled") is False,
    "historical_replay_disabled": flags.get("historical_replay_enabled") is False,
    "simulation_disabled": flags.get("simulation_enabled") is False,
    "live_execution_disabled": flags.get("live_execution_enabled") is False,
    "broker_execution_disabled": flags.get("broker_execution_enabled") is False,
    "registry_write_disabled": flags.get("registry_write_enabled") is False,
    "live_trade_still_blocked": '"status":"blocked"' in steps["blocked_live_trade"]["stdout"].replace(" ", ""),
}

certified = all(checks.values())

report = {
    "phase": "29E_HISTORICAL_REPLAY_MARKET_DATA_PROVIDER_CONTRACT_CERTIFICATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "certified": certified,
    "checks": checks,
    "steps": steps,
    "outputs": {
        "contract_json": str(contract_path),
        "contract_txt": str(txt_path),
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
