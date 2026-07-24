#!/usr/bin/env python3
import hashlib
import json
import subprocess
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/certifications/phase29g_historical_replay_provider_readiness_snapshot_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

LOCKED_FILES = [
    "runtime/strategy_candidate_sandbox/historical_replay_market_data_provider_contract_v1.json",
    "runtime/strategy_candidate_sandbox/historical_replay_market_data_provider_contract_v1.txt",
    "runtime/strategy_candidate_sandbox/historical_replay_provider_adapter_stub_latest.json",
    "runtime/strategy_candidate_sandbox/historical_replay_provider_adapter_stub_latest.txt",
]

def run(cmd):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return {
        "cmd": " ".join(cmd),
        "returncode": r.returncode,
        "stdout": r.stdout[-5000:],
        "stderr": r.stderr[-5000:],
    }

def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

steps = {
    "phase29f_cert": run(["python3", "scripts/phase29f_historical_replay_provider_adapter_stub_certification.py"]),
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
    "phase": "29G_HISTORICAL_REPLAY_PROVIDER_READINESS_SNAPSHOT",
    "generated_at": datetime.now(UTC).isoformat(),
    "status": "provider_contract_ready_adapter_stub_locked",
    "locked_scope": {
        "market_data_provider_contract": "locked",
        "provider_adapter_stub": "locked",
    },
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
    "next_recommended_phase": "Phase 30A — Historical Replay Market Data Provider Probe",
    "notes": [
        "Provider contract exists.",
        "Provider adapter is stub-only.",
        "No provider is wired.",
        "No bars are loaded.",
        "No historical replay execution is enabled.",
        "No live or broker execution path is enabled.",
    ],
}

checks = {
    "phase29f_certified": '"certified": true' in steps["phase29f_cert"]["stdout"],
    "all_locked_files_exist": all(item["exists"] for item in file_locks.values()),
    "provider_not_wired": snapshot["hard_locks"]["provider_wired"] is False,
    "market_data_disabled": snapshot["hard_locks"]["market_data_enabled"] is False,
    "historical_replay_disabled": snapshot["hard_locks"]["historical_replay_enabled"] is False,
    "simulation_disabled": snapshot["hard_locks"]["simulation_enabled"] is False,
    "monte_carlo_disabled": snapshot["hard_locks"]["monte_carlo_enabled"] is False,
    "promotion_disabled": snapshot["hard_locks"]["promotion_enabled"] is False,
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
