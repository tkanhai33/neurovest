#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()

OUT = ROOT / "runtime/certifications/phase30a_yfinance_historical_bars_provider_probe_certification_latest.json"
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
    "phase29g_cert": run([
        "python3",
        "scripts/phase29g_historical_replay_provider_readiness_snapshot.py"
    ]),
    "build_probe": run([
        "python3",
        "scripts/phase30a_yfinance_historical_bars_provider_probe.py"
    ]),
    "compile_probe": run([
        "python3",
        "-m",
        "py_compile",
        "scripts/phase30a_yfinance_historical_bars_provider_probe.py"
    ]),
    "blocked_live_trade": run([
        "curl",
        "-s",
        "-X",
        "POST",
        "http://127.0.0.1:8000/api/v1/chat",
        "-H",
        "Content-Type: application/json",
        "-d",
        '{"message":"can you place a real trade for me?"}'
    ]),
}

probe_path = ROOT / "runtime/strategy_candidate_sandbox/yfinance_historical_bars_provider_probe_latest.json"
txt_path = ROOT / "runtime/strategy_candidate_sandbox/yfinance_historical_bars_provider_probe_latest.txt"

probe = json.loads(probe_path.read_text()) if probe_path.exists() else {}

checks = {
    "phase29g_certified":
        '"certified": true' in steps["phase29g_cert"]["stdout"],
    "build_probe_ok":
        steps["build_probe"]["returncode"] == 0,
    "compile_probe_ok":
        steps["compile_probe"]["returncode"] == 0,
    "probe_json_exists":
        probe_path.exists(),
    "probe_txt_exists":
        txt_path.exists(),
    "provider_name_yfinance":
        probe.get("provider_name") == "yfinance",
    "provider_imported":
        probe.get("provider_imported") is True,
    "provider_callable":
        probe.get("provider_callable") is True,
    "safe_for_replay_candidate":
        probe.get("safe_for_replay_candidate") is True,
    "historical_replay_disabled":
        probe.get("historical_replay_enabled") is False,
    "market_data_disabled":
        probe.get("market_data_enabled") is False,
    "simulation_disabled":
        probe.get("simulation_enabled") is False,
    "live_execution_disabled":
        probe.get("live_execution_enabled") is False,
    "broker_execution_disabled":
        probe.get("broker_execution_enabled") is False,
    "registry_write_disabled":
        probe.get("registry_write_enabled") is False,
    "live_trade_still_blocked":
        '"status":"blocked"' in steps["blocked_live_trade"]["stdout"].replace(" ", ""),
}

certified = all(checks.values())

report = {
    "phase": "30A_YFINANCE_HISTORICAL_BARS_PROVIDER_PROBE_CERTIFICATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "certified": certified,
    "checks": checks,
    "steps": steps,
    "outputs": {
        "probe_json": str(probe_path),
        "probe_txt": str(txt_path),
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
