#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/certifications/phase30e_yfinance_historical_bars_adapter_shape_validation_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

def run(cmd, cwd=ROOT):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return {"cmd": " ".join(cmd), "returncode": r.returncode, "stdout": r.stdout[-5000:], "stderr": r.stderr[-5000:]}

steps = {
    "phase30d_cert": run(["python3", "scripts/phase30d_yfinance_historical_bars_adapter_stub_certification.py"]),
    "validate_shape": run(["python3", "scripts/phase30e_yfinance_historical_bars_adapter_shape_validation.py"]),
    "compile_validation": run(["python3", "-m", "py_compile", "scripts/phase30e_yfinance_historical_bars_adapter_shape_validation.py"]),
    "blocked_live_trade": run([
        "curl", "-s", "-X", "POST", "http://127.0.0.1:8000/api/v1/chat",
        "-H", "Content-Type: application/json",
        "-d", '{"message":"can you place a real trade for me?"}',
    ]),
}

validation_path = ROOT / "runtime/strategy_candidate_sandbox/yfinance_historical_bars_adapter_shape_validation_latest.json"
txt_path = ROOT / "runtime/strategy_candidate_sandbox/yfinance_historical_bars_adapter_shape_validation_latest.txt"

validation = json.loads(validation_path.read_text()) if validation_path.exists() else {}
shape = validation.get("shape_checks", {})
locks = validation.get("lock_checks", {})

checks = {
    "phase30d_certified": '"certified": true' in steps["phase30d_cert"]["stdout"],
    "validate_shape_ok": steps["validate_shape"]["returncode"] == 0,
    "compile_validation_ok": steps["compile_validation"]["returncode"] == 0,
    "validation_json_exists": validation_path.exists(),
    "validation_txt_exists": txt_path.exists(),
    "certified_shape_true": validation.get("certified_shape") is True,
    "top_level_is_dict": shape.get("top_level_is_dict") is True,
    "has_required_top_fields": shape.get("has_required_top_fields") is True,
    "provider_yfinance": shape.get("provider_yfinance") is True,
    "bars_is_list": shape.get("bars_is_list") is True,
    "bar_count_is_integer": shape.get("bar_count_is_integer") is True,
    "bar_count_matches_len": shape.get("bar_count_matches_len") is True,
    "status_not_wired": shape.get("status_not_wired") is True,
    "execution_flags_present": shape.get("execution_flags_present") is True,
    "provider_wired_false": locks.get("provider_wired_false") is True,
    "market_data_enabled_false": locks.get("market_data_enabled_false") is True,
    "historical_replay_enabled_false": locks.get("historical_replay_enabled_false") is True,
    "simulation_enabled_false": locks.get("simulation_enabled_false") is True,
    "live_execution_enabled_false": locks.get("live_execution_enabled_false") is True,
    "broker_execution_enabled_false": locks.get("broker_execution_enabled_false") is True,
    "registry_write_enabled_false": locks.get("registry_write_enabled_false") is True,
    "live_trade_still_blocked": '"status":"blocked"' in steps["blocked_live_trade"]["stdout"].replace(" ", ""),
}

certified = all(checks.values())

report = {
    "phase": "30E_YFINANCE_HISTORICAL_BARS_ADAPTER_SHAPE_VALIDATION_CERTIFICATION",
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
