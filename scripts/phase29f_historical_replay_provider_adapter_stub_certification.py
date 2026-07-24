#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/certifications/phase29f_historical_replay_provider_adapter_stub_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

def run(cmd, cwd=ROOT):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return {"cmd": " ".join(cmd), "returncode": r.returncode, "stdout": r.stdout[-5000:], "stderr": r.stderr[-5000:]}

steps = {
    "phase29e_cert": run(["python3", "scripts/phase29e_historical_replay_market_data_provider_contract_certification.py"]),
    "build_adapter": run(["python3", "scripts/phase29f_historical_replay_provider_adapter_stub.py"]),
    "compile_adapter": run(["python3", "-m", "py_compile", "scripts/phase29f_historical_replay_provider_adapter_stub.py"]),
    "blocked_live_trade": run([
        "curl", "-s", "-X", "POST", "http://127.0.0.1:8000/api/v1/chat",
        "-H", "Content-Type: application/json",
        "-d", '{"message":"can you place a real trade for me?"}',
    ]),
}

adapter_path = ROOT / "runtime/strategy_candidate_sandbox/historical_replay_provider_adapter_stub_latest.json"
txt_path = ROOT / "runtime/strategy_candidate_sandbox/historical_replay_provider_adapter_stub_latest.txt"

adapter = json.loads(adapter_path.read_text()) if adapter_path.exists() else {}
shape = adapter.get("stub_response_shape", {})

checks = {
    "phase29e_certified": '"certified": true' in steps["phase29e_cert"]["stdout"],
    "build_adapter_ok": steps["build_adapter"]["returncode"] == 0,
    "compile_adapter_ok": steps["compile_adapter"]["returncode"] == 0,
    "adapter_json_exists": adapter_path.exists(),
    "adapter_txt_exists": txt_path.exists(),
    "adapter_status_stub_only": adapter.get("adapter_status") == "stub_only",
    "required_function_declared": adapter.get("required_function") == "get_historical_bars",
    "provider_not_wired": adapter.get("provider_wired") is False,
    "market_data_disabled": adapter.get("market_data_enabled") is False,
    "historical_replay_disabled": adapter.get("historical_replay_enabled") is False,
    "simulation_disabled": adapter.get("simulation_enabled") is False,
    "live_execution_disabled": adapter.get("live_execution_enabled") is False,
    "broker_execution_disabled": adapter.get("broker_execution_enabled") is False,
    "registry_write_disabled": adapter.get("registry_write_enabled") is False,
    "stub_bars_empty": shape.get("bars") == [],
    "stub_bar_count_zero": shape.get("bar_count") == 0,
    "stub_status_not_wired": shape.get("status") == "not_wired",
    "live_trade_still_blocked": '"status":"blocked"' in steps["blocked_live_trade"]["stdout"].replace(" ", ""),
}

certified = all(checks.values())

report = {
    "phase": "29F_HISTORICAL_REPLAY_PROVIDER_ADAPTER_STUB_CERTIFICATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "certified": certified,
    "checks": checks,
    "steps": steps,
    "outputs": {
        "adapter_json": str(adapter_path),
        "adapter_txt": str(txt_path),
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
