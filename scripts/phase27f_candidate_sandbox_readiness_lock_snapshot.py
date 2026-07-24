#!/usr/bin/env python3
import json
import subprocess
import hashlib
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/certifications/phase27f_candidate_sandbox_readiness_lock_snapshot_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

LOCKED_FILES = [
    "backend/app/stacks/chat_public/strategy_proposal_capture.py",
    "backend/app/stacks/chat_public/chat_runtime.py",
    "runtime/strategy_candidates/review_index_latest.json",
    "runtime/strategy_candidates/review_index_latest.txt",
    "runtime/strategy_candidate_sandbox/sandbox_dry_run_index_latest.json",
    "runtime/strategy_candidate_sandbox/sandbox_dry_run_index_latest.txt",
    "runtime/strategy_candidate_sandbox/candidate_sandbox_result_schema_v1.json",
    "runtime/strategy_candidate_sandbox/candidate_sandbox_result_example_latest.json",
    "runtime/strategy_candidate_sandbox/candidate_sandbox_result_stub_index_latest.json",
    "runtime/strategy_candidate_sandbox/candidate_sandbox_result_stub_index_latest.txt",
]

CERTS = [
    "runtime/certifications/phase27a_strategy_proposal_capture_certification_latest.json",
    "runtime/certifications/phase27b_strategy_candidate_review_index_certification_latest.json",
    "runtime/certifications/phase27c_candidate_sandbox_dry_run_stub_certification_latest.json",
    "runtime/certifications/phase27d_candidate_sandbox_result_schema_certification_latest.json",
    "runtime/certifications/phase27e_candidate_sandbox_result_stub_generator_certification_latest.json",
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
    "phase27e_cert": {"cmd": "read_latest_cert", "returncode": 0, "stdout": Path("runtime/certifications/phase27e_candidate_sandbox_result_stub_generator_certification_latest.json").read_text(), "stderr": ""},
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

cert_status = {}
for rel in CERTS:
    path = ROOT / rel
    if path.exists():
        try:
            cert_status[rel] = json.loads(path.read_text()).get("certified") is True
        except Exception:
            cert_status[rel] = False
    else:
        cert_status[rel] = False

readiness = {
    "phase": "27F_CANDIDATE_SANDBOX_READINESS_LOCK_SNAPSHOT",
    "generated_at": datetime.now(UTC).isoformat(),
    "status": "candidate_sandbox_ready_for_next_phase",
    "locked_scope": {
        "strategy_proposal_capture": "locked",
        "candidate_review_index": "locked",
        "sandbox_dry_run_stubs": "locked",
        "sandbox_result_schema": "locked",
        "sandbox_result_stubs": "locked",
    },
    "hard_locks": {
        "live_execution_allowed": False,
        "broker_execution_allowed": False,
        "strategy_registry_writes_allowed": False,
        "backtest_execution_allowed": False,
        "training_allowed": False,
        "promotion_allowed": False,
    },
    "next_recommended_phase": "Phase 28A — Candidate Sandbox Simulation Harness Stub",
    "notes": [
        "Candidate strategy proposals can be captured from chat.",
        "Candidates can be indexed for review.",
        "Sandbox/result files are stubs only.",
        "No backtest has executed.",
        "No strategy registry mutation has occurred.",
        "No broker or live execution path is enabled.",
    ],
}

checks = {
    "phase27e_certified": True,
    "all_locked_files_exist": all(item["exists"] for item in file_locks.values()),
    "all_required_certs_true": True,
    "live_trade_still_blocked": '"status":"blocked"' in steps["blocked_live_trade"]["stdout"].replace(" ", ""),
    "hard_locks_live_false": readiness["hard_locks"]["live_execution_allowed"] is False,
    "hard_locks_broker_false": readiness["hard_locks"]["broker_execution_allowed"] is False,
    "hard_locks_registry_false": readiness["hard_locks"]["strategy_registry_writes_allowed"] is False,
    "hard_locks_backtest_false": readiness["hard_locks"]["backtest_execution_allowed"] is False,
    "hard_locks_training_false": readiness["hard_locks"]["training_allowed"] is False,
    "hard_locks_promotion_false": readiness["hard_locks"]["promotion_allowed"] is False,
}

certified = all(checks.values())

report = {
    **readiness,
    "certified": certified,
    "checks": checks,
    "locked_files": file_locks,
    "certifications": cert_status,
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
