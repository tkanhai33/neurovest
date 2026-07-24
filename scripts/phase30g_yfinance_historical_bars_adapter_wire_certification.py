#!/usr/bin/env python3
import json, subprocess, sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/certifications/phase30g_yfinance_historical_bars_adapter_wire_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

def run(cmd, cwd=ROOT):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return {"cmd": " ".join(cmd), "returncode": r.returncode, "stdout": r.stdout[-5000:], "stderr": r.stderr[-5000:]}

steps = {
    "phase30f_cert": run(["python3", "scripts/phase30f_yfinance_historical_bars_adapter_wire_preview_certification.py"]),
    "wire": run(["python3", "scripts/phase30g_yfinance_historical_bars_adapter_wire.py"]),
    "compile_adapter": run(["python3", "-m", "py_compile", "backend/app/stacks/market_data/yfinance_historical_bars_adapter.py"]),
    "adapter_unit": run([
        "python3", "-c",
        "from backend.app.stacks.market_data.yfinance_historical_bars_adapter import get_historical_bars; import json; print(json.dumps(get_historical_bars('AAPL','2024-01-01','2024-02-01','1d'), indent=2))"
    ]),
    "blocked_live_trade": run([
        "curl", "-s", "-X", "POST", "http://127.0.0.1:8000/api/v1/chat",
        "-H", "Content-Type: application/json",
        "-d", '{"message":"can you place a real trade for me?"}',
    ]),
}

unit = steps["adapter_unit"]["stdout"]
try:
    payload = json.loads(unit)
except Exception:
    payload = {}

flags = payload.get("execution_flags", {})

checks = {
    "phase30f_certified": '"certified": true' in steps["phase30f_cert"]["stdout"],
    "wire_ok": steps["wire"]["returncode"] == 0,
    "compile_adapter_ok": steps["compile_adapter"]["returncode"] == 0,
    "adapter_unit_ok": steps["adapter_unit"]["returncode"] == 0,
    "provider_yfinance": payload.get("provider") == "yfinance",
    "bars_is_list": isinstance(payload.get("bars"), list),
    "bar_count_integer": isinstance(payload.get("bar_count"), int),
    "bar_count_matches": payload.get("bar_count") == len(payload.get("bars", [])),
    "provider_wired_true": flags.get("provider_wired") is True,
    "market_data_enabled_true": flags.get("market_data_enabled") is True,
    "historical_replay_disabled": flags.get("historical_replay_enabled") is False,
    "simulation_disabled": flags.get("simulation_enabled") is False,
    "live_execution_disabled": flags.get("live_execution_enabled") is False,
    "broker_execution_disabled": flags.get("broker_execution_enabled") is False,
    "registry_write_disabled": flags.get("registry_write_enabled") is False,
    "live_trade_still_blocked": '"status":"blocked"' in steps["blocked_live_trade"]["stdout"].replace(" ", ""),
}

certified = all(checks.values())

report = {
    "phase": "30G_YFINANCE_HISTORICAL_BARS_ADAPTER_WIRE_CERTIFICATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "certified": certified,
    "checks": checks,
    "sample": payload,
    "steps": steps,
}

OUT.write_text(json.dumps(report, indent=2))

print(json.dumps({"phase": report["phase"], "certified": certified, "checks": checks, "output": str(OUT)}, indent=2))

if not certified:
    sys.exit(1)
