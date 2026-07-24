#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/certifications/phase30d_yfinance_historical_bars_adapter_stub_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

def run(cmd, cwd=ROOT):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return {"cmd": " ".join(cmd), "returncode": r.returncode, "stdout": r.stdout[-5000:], "stderr": r.stderr[-5000:]}

steps = {
    "phase30c_cert": run(["python3", "scripts/phase30c_historical_bars_contract_certification.py"]),
    "build_adapter": run(["python3", "scripts/phase30d_yfinance_historical_bars_adapter_stub.py"]),
    "compile_adapter": run(["python3", "-m", "py_compile", "backend/app/stacks/market_data/yfinance_historical_bars_adapter.py"]),
    "adapter_unit": run([
        "python3", "-c",
        "from backend.app.stacks.market_data.yfinance_historical_bars_adapter import get_historical_bars; import json; print(json.dumps(get_historical_bars('AAPL','2024-01-01','2024-02-01'), indent=2))"
    ]),
    "blocked_live_trade": run([
        "curl", "-s", "-X", "POST", "http://127.0.0.1:8000/api/v1/chat",
        "-H", "Content-Type: application/json",
        "-d", '{"message":"can you place a real trade for me?"}',
    ]),
}

adapter_path = ROOT / "backend/app/stacks/market_data/yfinance_historical_bars_adapter.py"
snapshot_path = ROOT / "runtime/strategy_candidate_sandbox/yfinance_historical_bars_adapter_stub_latest.json"
txt_path = ROOT / "runtime/strategy_candidate_sandbox/yfinance_historical_bars_adapter_stub_latest.txt"

snapshot = json.loads(snapshot_path.read_text()) if snapshot_path.exists() else {}
unit = steps["adapter_unit"]["stdout"]

checks = {
    "phase30c_certified": '"certified": true' in steps["phase30c_cert"]["stdout"],
    "build_adapter_ok": steps["build_adapter"]["returncode"] == 0,
    "compile_adapter_ok": steps["compile_adapter"]["returncode"] == 0,
    "adapter_file_exists": adapter_path.exists(),
    "snapshot_json_exists": snapshot_path.exists(),
    "snapshot_txt_exists": txt_path.exists(),
    "adapter_status_stub_only": snapshot.get("adapter_status") == "stub_only",
    "selected_provider_yfinance": snapshot.get("selected_provider") == "yfinance",
    "required_function_exists": "def get_historical_bars" in adapter_path.read_text(),
    "adapter_unit_ok": steps["adapter_unit"]["returncode"] == 0,
    "adapter_returns_yfinance": '"provider": "yfinance"' in unit,
    "adapter_returns_empty_bars": '"bars": []' in unit,
    "adapter_returns_bar_count_zero": '"bar_count": 0' in unit,
    "adapter_returns_not_wired": '"status": "not_wired"' in unit,
    "provider_not_wired": snapshot.get("provider_wired") is False,
    "market_data_disabled": snapshot.get("market_data_enabled") is False,
    "historical_replay_disabled": snapshot.get("historical_replay_enabled") is False,
    "simulation_disabled": snapshot.get("simulation_enabled") is False,
    "live_execution_disabled": snapshot.get("live_execution_enabled") is False,
    "broker_execution_disabled": snapshot.get("broker_execution_enabled") is False,
    "registry_write_disabled": snapshot.get("registry_write_enabled") is False,
    "live_trade_still_blocked": '"status":"blocked"' in steps["blocked_live_trade"]["stdout"].replace(" ", ""),
}

certified = all(checks.values())

report = {
    "phase": "30D_YFINANCE_HISTORICAL_BARS_ADAPTER_STUB_CERTIFICATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "certified": certified,
    "checks": checks,
    "steps": steps,
    "outputs": {
        "adapter": str(adapter_path),
        "snapshot_json": str(snapshot_path),
        "snapshot_txt": str(txt_path),
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
