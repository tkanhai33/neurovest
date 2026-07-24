#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/certifications/phase31a_historical_bars_fetch_validation_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

def run(cmd, cwd=ROOT):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return {"cmd": " ".join(cmd), "returncode": r.returncode, "stdout": r.stdout[-5000:], "stderr": r.stderr[-5000:]}

steps = {
    "phase30g_cert": run(["python3", "scripts/phase30g_yfinance_historical_bars_adapter_wire_certification.py"]),
    "fetch_validate": run(["python3", "scripts/phase31a_historical_bars_fetch_validation.py"]),
    "compile_validation": run(["python3", "-m", "py_compile", "scripts/phase31a_historical_bars_fetch_validation.py"]),
    "blocked_live_trade": run([
        "curl", "-s", "-X", "POST", "http://127.0.0.1:8000/api/v1/chat",
        "-H", "Content-Type: application/json",
        "-d", '{"message":"can you place a real trade for me?"}',
    ]),
}

validation_path = ROOT / "runtime/strategy_candidate_sandbox/historical_bars_fetch_validation_latest.json"
txt_path = ROOT / "runtime/strategy_candidate_sandbox/historical_bars_fetch_validation_latest.txt"

validation = json.loads(validation_path.read_text()) if validation_path.exists() else {}
checks = validation.get("checks", {})

cert_checks = {
    "phase30g_certified": '"certified": true' in steps["phase30g_cert"]["stdout"],
    "fetch_validate_ok": steps["fetch_validate"]["returncode"] == 0,
    "compile_validation_ok": steps["compile_validation"]["returncode"] == 0,
    "validation_json_exists": validation_path.exists(),
    "validation_txt_exists": txt_path.exists(),
    "validated_true": validation.get("validated") is True,
    "provider_yfinance": checks.get("provider_yfinance") is True,
    "status_ok": checks.get("status_ok") is True,
    "bars_is_list": checks.get("bars_is_list") is True,
    "bar_count_positive": checks.get("bar_count_positive") is True,
    "bar_count_matches_len": checks.get("bar_count_matches_len") is True,
    "all_bars_valid": checks.get("all_bars_valid") is True,
    "provider_wired_true": checks.get("provider_wired_true") is True,
    "market_data_enabled_true": checks.get("market_data_enabled_true") is True,
    "historical_replay_disabled": checks.get("historical_replay_disabled") is True,
    "simulation_disabled": checks.get("simulation_disabled") is True,
    "live_execution_disabled": checks.get("live_execution_disabled") is True,
    "broker_execution_disabled": checks.get("broker_execution_disabled") is True,
    "registry_write_disabled": checks.get("registry_write_disabled") is True,
    "live_trade_still_blocked": '"status":"blocked"' in steps["blocked_live_trade"]["stdout"].replace(" ", ""),
}

certified = all(cert_checks.values())

report = {
    "phase": "31A_HISTORICAL_BARS_FETCH_VALIDATION_CERTIFICATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "certified": certified,
    "checks": cert_checks,
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
    "checks": cert_checks,
    "output": str(OUT),
}, indent=2))

if not certified:
    sys.exit(1)
