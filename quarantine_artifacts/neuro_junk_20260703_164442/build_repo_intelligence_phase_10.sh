#!/bin/bash
set -e

echo "🧠 Phase 10 — Governance + Policy Enforcement Layer"

mkdir -p backend/app/spine/L4_runtime/governance
mkdir -p backend/app/spine/L5_api
mkdir -p backend/app/spine/L7_tests

# =========================================================
# FILE 1 — GOVERNANCE POLICY ENGINE
# =========================================================
cat > backend/app/spine/L4_runtime/governance/policy_engine.py <<'PY'
from __future__ import annotations

from spine.L4_runtime.repo_intelligence_engine import build_repo_intelligence

FORBIDDEN_CROSS_STACK_WRITES = {
    "risk": ["execution", "portfolio"],
    "execution": ["risk"],
    "auth_identity": ["execution"],
}

def evaluate_policy(proposal: dict) -> dict:
    """
    Validates whether a structural change is allowed.
    """

    stack = proposal.get("stack")
    target = proposal.get("target")

    violations = []

    if stack in FORBIDDEN_CROSS_STACK_WRITES:
        if target in FORBIDDEN_CROSS_STACK_WRITES[stack]:
            violations.append({
                "type": "FORBIDDEN_CROSS_STACK_WRITE",
                "stack": stack,
                "target": target
            })

    return {
        "allowed": len(violations) == 0,
        "violations": violations
    }
PY


# =========================================================
# FILE 2 — CHANGE PROPOSAL SYSTEM
# =========================================================
cat > backend/app/spine/L4_runtime/governance/change_proposal_engine.py <<'PY'
from __future__ import annotations

from spine.L4_runtime.architecture_repair_engine import detect_repair_actions
from spine.L4_runtime.gap_reconciliation_engine import reconcile_gaps

def generate_change_proposals(limit: int = 1000) -> dict:
    """
    EVERYTHING becomes a proposal first.
    NOTHING is executed directly.
    """

    repairs = detect_repair_actions(limit=limit)
    gaps = reconcile_gaps(limit=limit)

    proposals = []

    for r in repairs["repairs"]:
        proposals.append({
            "type": "REPAIR_PROPOSAL",
            "stack": r["stack"],
            "target": r.get("target"),
            "action": r["action"]
        })

    for stack, items in gaps["corrected_gaps"].items():
        proposals.append({
            "type": "GAP_PROPOSAL",
            "stack": stack,
            "target": items
        })

    return {
        "proposal_count": len(proposals),
        "proposals": proposals
    }
PY


# =========================================================
# FILE 3 — COMMIT GATE (FINAL AUTHORITY LAYER)
# =========================================================
cat > backend/app/spine/L4_runtime/governance/commit_gate.py <<'PY'
from __future__ import annotations

from spine.L4_runtime.governance.policy_engine import evaluate_policy
from spine.L4_runtime.governance.change_proposal_engine import generate_change_proposals

def validate_commit(limit: int = 1000) -> dict:
    """
    FINAL GATE BEFORE ANY STRUCTURAL CHANGE.
    """

    proposals = generate_change_proposals(limit=limit)["proposals"]

    allowed = []
    blocked = []

    for p in proposals:
        result = evaluate_policy(p)

        if result["allowed"]:
            allowed.append(p)
        else:
            blocked.append({
                "proposal": p,
                "reason": result["violations"]
            })

    return {
        "allowed_count": len(allowed),
        "blocked_count": len(blocked),
        "commit_allowed": len(blocked) == 0,
        "blocked": blocked
    }
PY


# =========================================================
# FILE 4 — GOVERNED CLI (PHASE 10 CONTROL SYSTEM)
# =========================================================
cat > backend/app/spine/L5_api/repo_intelligence_v10_cli.py <<'PY'
from __future__ import annotations

import json

from spine.L4_runtime.repo_intelligence_engine import build_repo_intelligence
from spine.L4_runtime.convergence_engine import check_convergence
from spine.L4_runtime.governance.change_proposal_engine import generate_change_proposals
from spine.L4_runtime.governance.commit_gate import validate_commit

def run(limit: int = 1000):
    report = {
        "repo_intelligence": build_repo_intelligence(limit=limit),
        "convergence": check_convergence(limit=limit),

        # GOVERNANCE LAYER
        "proposals": generate_change_proposals(limit=limit),
        "commit_gate": validate_commit(limit=limit),
    }

    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    run()
PY


# =========================================================
# FILE 5 — GOVERNANCE TESTS
# =========================================================
cat > backend/app/spine/L7_tests/test_phase10_governance.py <<'PY'
from spine.L4_runtime.governance.policy_engine import evaluate_policy
from spine.L4_runtime.governance.commit_gate import validate_commit
from spine.L4_runtime.governance.change_proposal_engine import generate_change_proposals

def test_policy_engine_runs():
    r = evaluate_policy({"stack": "risk", "target": "execution"})
    assert "allowed" in r

def test_proposal_generation():
    p = generate_change_proposals(limit=200)
    assert "proposals" in p

def test_commit_gate_runs():
    c = validate_commit(limit=200)
    assert "commit_allowed" in c
PY


# =========================================================
# EXECUTION
# =========================================================

echo "🧠 Running Phase 10 CLI..."
PYTHONPATH=backend/app python3 backend/app/spine/L5_api/repo_intelligence_v10_cli.py

echo "🧪 Running Phase 10 tests..."
PYTHONPATH=backend/app pytest -q backend/app/spine/L7_tests/test_phase10_governance.py

echo "✅ Phase 10 Complete"
