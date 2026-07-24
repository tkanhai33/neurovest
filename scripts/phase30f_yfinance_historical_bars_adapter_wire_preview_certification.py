#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/certifications/phase30f_yfinance_historical_bars_adapter_wire_preview_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

def run(cmd, cwd=ROOT):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return {"cmd": " ".join(cmd), "returncode": r.returncode, "stdout": r.stdout[-5000:], "stderr": r.stderr[-5000:]}

steps = {
    "phase30e_cert": run(["python3", "scripts/phase30e_yfinance_historical_bars_adapter_shape_validation_certification.py"]),
    "build_preview": run(["python3", "scripts/phase30f_yfinance_historical_bars_adapter_wire_preview.py"]),
    "compile_preview": run(["python3", "-m", "py_compile", "scripts/phase30f_yfinance_historical_bars_adapter_wire_preview.py"]),
    "blocked_live_trade": run([
        "curl", "-s", "-X", "POST", "http://127.0.0.1:8000/api/v1/chat",
        "-H", "Content-Type: application/json",
        "-d", '{"message":"can you place a real trade for me?"}',
    ]),
}

preview_path = ROOT / "runtime/strategy_candidate_sandbox/yfinance_historical_bars_adapter_wire_preview_latest.json"
txt_path = ROOT / "runtime/strategy_candidate_sandbox/yfinance_historical_bars_adapter_wire_preview_latest.txt"

preview = json.loads(preview_path.read_text()) if preview_path.exists() else {}
proposed = preview.get("proposed_change", {})
locks = preview.get("hard_locks", {})

checks = {
    "phase30e_certified": '"certified": true' in steps["phase30e_cert"]["stdout"],
    "build_preview_ok": steps["build_preview"]["returncode"] == 0,
    "compile_preview_ok": steps["compile_preview"]["returncode"] == 0,
    "preview_json_exists": preview_path.exists(),
    "preview_txt_exists": txt_path.exists(),
    "wire_status_preview_only": preview.get("wire_status") == "preview_only",
    "selected_provider_yfinance": preview.get("selected_provider") == "yfinance",
    "target_function_get_historical_bars": preview.get("target_function") == "get_historical_bars",
    "proposes_provider_wired": proposed.get("provider_wired") is True,
    "proposes_market_data_enabled": proposed.get("market_data_enabled") is True,
    "proposed_historical_replay_still_disabled": proposed.get("historical_replay_enabled") is False,
    "proposed_simulation_still_disabled": proposed.get("simulation_enabled") is False,
    "proposed_live_execution_disabled": proposed.get("live_execution_enabled") is False,
    "proposed_broker_execution_disabled": proposed.get("broker_execution_enabled") is False,
    "proposed_registry_write_disabled": proposed.get("registry_write_enabled") is False,
    "hard_lock_historical_replay_false": locks.get("historical_replay_enabled") is False,
    "hard_lock_simulation_false": locks.get("simulation_enabled") is False,
    "hard_lock_live_false": locks.get("live_execution_enabled") is False,
    "hard_lock_broker_false": locks.get("broker_execution_enabled") is False,
    "hard_lock_registry_false": locks.get("registry_write_enabled") is False,
    "live_trade_still_blocked": '"status":"blocked"' in steps["blocked_live_trade"]["stdout"].replace(" ", ""),
}

certified = all(checks.values())

report = {
    "phase": "30F_YFINANCE_HISTORICAL_BARS_ADAPTER_WIRE_PREVIEW_CERTIFICATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "certified": certified,
    "checks": checks,
    "steps": steps,
    "outputs": {
        "preview_json": str(preview_path),
        "preview_txt": str(txt_path),
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
