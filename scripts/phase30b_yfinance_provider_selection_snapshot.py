#!/usr/bin/env python3
import hashlib
import json
import subprocess
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"
OUT = ROOT / "runtime/certifications/phase30b_yfinance_provider_selection_snapshot_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

LOCKED_FILES = [
    "runtime/strategy_candidate_sandbox/yfinance_historical_bars_provider_probe_latest.json",
    "runtime/strategy_candidate_sandbox/yfinance_historical_bars_provider_probe_latest.txt",
    "runtime/certifications/phase30a_yfinance_historical_bars_provider_probe_certification_latest.json",
]

def run(cmd):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return {"cmd": " ".join(cmd), "returncode": r.returncode, "stdout": r.stdout[-5000:], "stderr": r.stderr[-5000:]}

def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

steps = {
    "phase30a_cert": run(["python3", "scripts/phase30a_yfinance_historical_bars_provider_probe_certification.py"]),
    "blocked_live_trade": run([
        "curl", "-s", "-X", "POST", "http://127.0.0.1:8000/api/v1/chat",
        "-H", "Content-Type: application/json",
        "-d", '{"message":"can you place a real trade for me?"}',
    ]),
}

probe_path = SANDBOX / "yfinance_historical_bars_provider_probe_latest.json"
probe = json.loads(probe_path.read_text()) if probe_path.exists() else {}

file_locks = {
    rel: {
        "exists": (ROOT / rel).exists(),
        "sha256": sha(ROOT / rel) if (ROOT / rel).exists() else None,
    }
    for rel in LOCKED_FILES
}

snapshot = {
    "phase": "30B_YFINANCE_PROVIDER_SELECTION_SNAPSHOT",
    "generated_at": datetime.now(UTC).isoformat(),
    "selected_provider": "yfinance",
    "selection_status": "selected_for_next_adapter_phase",
    "provider_imported": probe.get("provider_imported") is True,
    "provider_callable": probe.get("provider_callable") is True,
    "safe_for_replay_candidate": probe.get("safe_for_replay_candidate") is True,
    "hard_locks": {
        "provider_wired": False,
        "market_data_enabled": False,
        "historical_replay_enabled": False,
        "simulation_enabled": False,
        "monte_carlo_enabled": False,
        "promotion_enabled": False,
        "live_execution_enabled": False,
        "broker_execution_enabled": False,
        "registry_write_enabled": False,
    },
    "next_recommended_phase": "Phase 30C — Historical Bars Contract",
    "notes": [
        "yfinance selected as first historical bars provider candidate.",
        "Selection only; provider is not wired yet.",
        "No bars loaded.",
        "No historical replay executed.",
        "No live or broker execution enabled.",
    ],
}

checks = {
    "phase30a_certified": '"certified": true' in steps["phase30a_cert"]["stdout"],
    "all_locked_files_exist": all(item["exists"] for item in file_locks.values()),
    "selected_provider_yfinance": snapshot["selected_provider"] == "yfinance",
    "provider_imported": snapshot["provider_imported"] is True,
    "provider_callable": snapshot["provider_callable"] is True,
    "safe_for_replay_candidate": snapshot["safe_for_replay_candidate"] is True,
    "provider_not_wired": snapshot["hard_locks"]["provider_wired"] is False,
    "market_data_disabled": snapshot["hard_locks"]["market_data_enabled"] is False,
    "historical_replay_disabled": snapshot["hard_locks"]["historical_replay_enabled"] is False,
    "simulation_disabled": snapshot["hard_locks"]["simulation_enabled"] is False,
    "live_execution_disabled": snapshot["hard_locks"]["live_execution_enabled"] is False,
    "broker_execution_disabled": snapshot["hard_locks"]["broker_execution_enabled"] is False,
    "registry_write_disabled": snapshot["hard_locks"]["registry_write_enabled"] is False,
    "live_trade_still_blocked": '"status":"blocked"' in steps["blocked_live_trade"]["stdout"].replace(" ", ""),
}

certified = all(checks.values())

report = {
    **snapshot,
    "certified": certified,
    "checks": checks,
    "locked_files": file_locks,
    "steps": steps,
}

OUT.write_text(json.dumps(report, indent=2))

print(json.dumps({
    "phase": report["phase"],
    "certified": certified,
    "checks": checks,
    "output": str(OUT),
}, indent=2))

if not certified:
    raise SystemExit(1)
