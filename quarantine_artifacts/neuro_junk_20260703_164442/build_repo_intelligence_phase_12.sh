#!/bin/bash
set -e

echo "🧠 Phase 12 — Closed Loop Execution Governor"

mkdir -p backend/app/spine/L4_runtime/governance
mkdir -p backend/app/spine/L4_runtime/sandbox
mkdir -p backend/app/spine/L5_api
mkdir -p backend/app/spine/L7_tests

# =========================================================
# FILE 1 — DECISION ENGINE (TRUTH MERGER)
# =========================================================
cat > backend/app/spine/L4_runtime/governance/decision_engine.py <<'PY'
from __future__ import annotations

from spine.L4_runtime.sandbox.simulation_engine import simulate_change
from spine.L4_runtime.governance.policy_engine import evaluate_policy

def evaluate_decision(proposal: dict) -> dict:
    """
    Merges simulation + policy into a single truth output.
    """

    sim = simulate_change(proposal)
    policy = evaluate_policy(proposal)

    score = sim["risk_score"]

    policy_block = not policy["allowed"]

    approved = (score <= 2) and (not policy_block)

    return {
        "proposal": proposal,
        "simulation": sim,
        "policy": policy,
        "final_score": score,
        "approved": approved,
        "reason": (
            "PASS" if approved
            else "FAILED_SIMULATION" if score > 2
            else "FAILED_POLICY"
        )
    }
PY


# =========================================================
# FILE 2 — APPROVAL STATE MACHINE
# =========================================================
cat > backend/app/spine/L4_runtime/governance/approval_state_machine.py <<'PY'
from __future__ import annotations

from spine.L4_runtime.governance.decision_engine import evaluate_decision

STATE_TRANSITIONS = {
    "PENDING": ["SIMULATED"],
    "SIMULATED": ["POLICY_CHECKED"],
    "POLICY_CHECKED": ["APPROVED", "REJECTED"],
}

def run_approval_flow(proposal: dict) -> dict:
    """
    Deterministic approval pipeline.
    """

    decision = evaluate_decision(proposal)

    if decision["approved"]:
        state = "APPROVED"
    else:
        state = "REJECTED"

    return {
        "state": state,
        "decision": decision
    }
PY


# =========================================================
# FILE 3 — GOVERNED EXECUTION LOG (NO EXECUTION)
# =========================================================
cat > backend/app/spine/L4_runtime/governance/execution_log.py <<'PY'
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

LOG_FILE = Path("backend/app/spine/L4_runtime/governance/decision_log.json")

def log_decision(entry: dict) -> None:
    """
    Pure audit trail — NO SIDE EFFECTS beyond logging.
    """

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    log = []

    if LOG_FILE.exists():
        try:
            log = json.loads(LOG_FILE.read_text())
        except Exception:
            log = []

    entry["timestamp"] = datetime.utcnow().isoformat()
    log.append(entry)

    LOG_FILE.write_text(json.dumps(log, indent=2))
PY


# =========================================================
# FILE 4 — GOVERNED CLI (PHASE 12 CORE)
# =========================================================
cat > backend/app/spine/L5_api/repo_intelligence_v12_cli.py <<'PY'
from __future__ import annotations

import json

from spine.L4_runtime.governance.change_proposal_engine import generate_change_proposals
from spine.L4_runtime.governance.approval_state_machine import run_approval_flow
from spine.L4_runtime.governance.execution_log import log_decision

def run(limit: int = 1000):
    proposals = generate_change_proposals(limit=limit)["proposals"]

    results = []

    for p in proposals:
        decision = run_approval_flow(p)
        log_decision(decision)
        results.append(decision)

    summary = {
        "total": len(results),
        "approved": sum(1 for r in results if r["state"] == "APPROVED"),
        "rejected": sum(1 for r in results if r["state"] == "REJECTED"),
        "results": results[:10]  # preview only
    }

    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    run()
PY


# =========================================================
# FILE 5 — PHASE 12 TESTS
# =========================================================
cat > backend/app/spine/L7_tests/test_phase12_governor.py <<'PY'
from spine.L4_runtime.governance.decision_engine import evaluate_decision
from spine.L4_runtime.governance.approval_state_machine import run_approval_flow

def test_decision_engine():
    r = evaluate_decision({"stack": "risk", "target": "limits"})
    assert "approved" in r

def test_approval_flow():
    r = run_approval_flow({"stack": "strategy", "target": "selector"})
    assert "state" in r
    assert r["state"] in ["APPROVED", "REJECTED"]
PY


# =========================================================
# EXECUTION
# =========================================================

echo "🧠 Running Phase 12 CLI..."
PYTHONPATH=backend/app python3 backend/app/spine/L5_api/repo_intelligence_v12_cli.py

echo "🧪 Running Phase 12 tests..."
PYTHONPATH=backend/app pytest -q backend/app/spine/L7_tests/test_phase12_governor.py

echo "✅ Phase 12 Complete"
