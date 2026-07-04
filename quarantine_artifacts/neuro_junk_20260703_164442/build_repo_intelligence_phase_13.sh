#!/bin/bash
set -e

echo "🧠 Phase 13 — Governed Action Enforcement Layer"

mkdir -p backend/app/spine/L4_runtime/governance
mkdir -p backend/app/spine/L5_api
mkdir -p backend/app/spine/L7_tests

# =========================================================
# FILE 1 — ACTION ENFORCEMENT ENGINE
# =========================================================
cat > backend/app/spine/L4_runtime/governance/action_enforcer.py <<'PY'
from __future__ import annotations

from spine.L4_runtime.governance.approval_state_machine import run_approval_flow

# in-memory state store (no persistence writes to system state)
SYSTEM_STATE = {
    "risk": "idle",
    "strategy": "idle",
    "execution": "idle",
    "portfolio": "idle"
}

def enforce_action(proposal: dict) -> dict:
    """
    Applies ONLY approved decisions to internal state.
    """

    result = run_approval_flow(proposal)

    stack = proposal.get("stack")
    target = proposal.get("target")

    if result["state"] == "APPROVED":
        SYSTEM_STATE[stack] = f"updated:{target}"
        action_taken = True
    else:
        action_taken = False

    return {
        "proposal": proposal,
        "state": result["state"],
        "action_taken": action_taken,
        "system_state_snapshot": dict(SYSTEM_STATE)
    }
PY


# =========================================================
# FILE 2 — STATE AUDITOR
# =========================================================
cat > backend/app/spine/L4_runtime/governance/state_auditor.py <<'PY'
from __future__ import annotations

from spine.L4_runtime.governance.action_enforcer import SYSTEM_STATE

def audit_state() -> dict:
    """
    Reads system state without modifying it.
    """

    return {
        "state_snapshot": dict(SYSTEM_STATE),
        "health": "stable"
    }
PY


# =========================================================
# FILE 3 — GOVERNED EXECUTION PIPELINE
# =========================================================
cat > backend/app/spine/L4_runtime/governance/governed_pipeline.py <<'PY'
from __future__ import annotations

from spine.L4_runtime.governance.change_proposal_engine import generate_change_proposals
from spine.L4_runtime.governance.action_enforcer import enforce_action

def run_governed_pipeline(limit: int = 1000) -> dict:
    proposals = generate_change_proposals(limit=limit)["proposals"]

    results = []

    for p in proposals:
        result = enforce_action(p)
        results.append(result)

    return {
        "total": len(results),
        "executed": sum(1 for r in results if r["action_taken"]),
        "skipped": sum(1 for r in results if not r["action_taken"]),
        "results": results[:10]
    }
PY


# =========================================================
# FILE 4 — CLI V13
# =========================================================
cat > backend/app/spine/L5_api/repo_intelligence_v13_cli.py <<'PY'
from __future__ import annotations

import json

from spine.L4_runtime.governance.change_proposal_engine import generate_change_proposals
from spine.L4_runtime.governance.state_auditor import audit_state
from spine.L4_runtime.governance.governed_pipeline import run_governed_pipeline

def run(limit: int = 1000):
    report = {
        "proposals": generate_change_proposals(limit=limit),
        "pipeline": run_governed_pipeline(limit=limit),
        "audit": audit_state(),
    }

    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    run()
PY


# =========================================================
# FILE 5 — PHASE 13 TESTS
# =========================================================
cat > backend/app/spine/L7_tests/test_phase13_enforcement.py <<'PY'
from spine.L4_runtime.governance.action_enforcer import enforce_action
from spine.L4_runtime.governance.state_auditor import audit_state

def test_enforcer_runs():
    r = enforce_action({"stack": "risk", "target": "limits"})
    assert "state" in r

def test_auditor_runs():
    r = audit_state()
    assert "state_snapshot" in r
PY


# =========================================================
# EXECUTION
# =========================================================

echo "🧠 Running Phase 13 CLI..."
PYTHONPATH=backend/app python3 backend/app/spine/L5_api/repo_intelligence_v13_cli.py

echo "🧪 Running Phase 13 tests..."
PYTHONPATH=backend/app pytest -q backend/app/spine/L7_tests/test_phase13_enforcement.py

echo "✅ Phase 13 Complete"
