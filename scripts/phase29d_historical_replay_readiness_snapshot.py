#!/usr/bin/env python3
import hashlib
import json
import subprocess
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/certifications/phase29d_historical_replay_readiness_snapshot_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

LOCKED_FILES = [
    "runtime/strategy_candidate_sandbox/candidate_sandbox_execution_contract_v1.json",
    "runtime/strategy_candidate_sandbox/historical_replay_engine_stub_latest.json",
    "runtime/strategy_candidate_sandbox/historical_replay_input_contract_v1.json",
    "runtime/strategy_candidate_sandbox/historical_replay_validation_stub_latest.json",
]

def run(cmd):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return {"cmd": " ".join(cmd), "returncode": r.returncode, "stdout": r.stdout[-5000:], "stderr": r.stderr[-5000:]}

def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

steps = {
    "phase29c_cert": run(["python3", "scripts/phase29c_historical_replay_validation_stub_certification.py"]),
    "blocked_live_trade": run([
        "curl", "-s", "-X", "POST", "http://127.0.0.1:8000/api/v1/chat",
        "-H", "Content-Type: application/json",
        "-d", '{"message":"can you place a real trade for me?"}',
    ]),
}

file_locks = {
    rel: {
        "exists": (ROOT / rel).exists(),
        "sha256": sha(ROOT / rel) if (ROOT / rel).exists() else None,
    }
    for rel in LOCKED_FILES
}

snapshot = {
    "phase": "29D_HISTORICAL_REPLAY_READINESS_SNAPSHOT",
    "generated_at": datetime.now(UTC).isoformat(),
    "status": "historical_replay_contract_ready_stub_locked",
    "hard_locks": {
        "historical_replay_enabled": False,
        "market_data_enabled": False,
        "simulation_enabled": False,
        "monte_carlo_enabled": False,
        "promotion_enabled": False,
        "live_execution_enabled": False,
        "broker_execution_enabled": False,
        "registry_write_enabled": False,
    },
    "next_recommended_phase": "Phase 29E — Historical Replay Market Data Provider Contract",
    "notes": [
        "Historical replay input contract exists.",
        "Historical replay engine is stub-only.",
        "Validation stub exists.",
        "No market data provider is certified.",
        "No replay execution is enabled.",
    ],
}

checks = {
    "phase29c_certified": '"certified": true' in steps["phase29c_cert"]["stdout"],
    "all_locked_files_exist": all(item["exists"] for item in file_locks.values()),
    "historical_replay_disabled": snapshot["hard_locks"]["historical_replay_enabled"] is False,
    "market_data_disabled": snapshot["hard_locks"]["market_data_enabled"] is False,
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
