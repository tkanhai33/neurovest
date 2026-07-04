#!/bin/bash
set -e

echo "🧠 Phase 11 — Execution Sandbox + Simulation Layer"

mkdir -p backend/app/spine/L4_runtime/sandbox
mkdir -p backend/app/spine/L5_api
mkdir -p backend/app/spine/L7_tests

# =========================================================
# FILE 1 — SANDBOX SIMULATION ENGINE
# =========================================================
cat > backend/app/spine/L4_runtime/sandbox/simulation_engine.py <<'PY'
from __future__ import annotations

from spine.L4_runtime.repo_intelligence_engine import build_repo_intelligence
from spine.L4_runtime.dependency_graph_engine import build_dependency_graph

def simulate_change(proposal: dict) -> dict:
    """
    Pure simulation: NO FILE WRITES.
    """

    stack = proposal.get("stack")
    target = proposal.get("target")

    intel = build_repo_intelligence(limit=1000)
    deps = build_dependency_graph(limit=1000)

    risk_score = 0

    # dependency pressure adds risk
    risk_score += len(deps.get("missing_links", {}).get(stack, []))

    # unknown stack penalty
    if stack not in intel["structure"]:
        risk_score += 2

    # forbidden structural zones
    if stack in ["execution", "risk"] and target in ["broker", "kill_switch"]:
        risk_score += 3

    return {
        "proposal": proposal,
        "risk_score": risk_score,
        "safe": risk_score <= 2,
        "recommendation": "commit" if risk_score <= 2 else "reject"
    }
PY


# =========================================================
# FILE 2 — SANDBOX BATCH RUNNER
# =========================================================
cat > backend/app/spine/L4_runtime/sandbox/simulation_batch_runner.py <<'PY'
from __future__ import annotations

from spine.L4_runtime.governance.change_proposal_engine import generate_change_proposals
from spine.L4_runtime.sandbox.simulation_engine import simulate_change

def run_sandbox(limit: int = 1000) -> dict:
    proposals = generate_change_proposals(limit=limit)["proposals"]

    results = []
    safe = []
    rejected = []

    for p in proposals:
        sim = simulate_change(p)
        results.append(sim)

        if sim["safe"]:
            safe.append(p)
        else:
            rejected.append(p)

    return {
        "total": len(proposals),
        "safe_count": len(safe),
        "rejected_count": len(rejected),
        "results": results
    }
PY


# =========================================================
# FILE 3 — SIMULATION-AWARE PLANNER
# =========================================================
cat > backend/app/spine/L4_runtime/sandbox/safe_commit_planner.py <<'PY'
from __future__ import annotations

from spine.L4_runtime.governance.change_proposal_engine import generate_change_proposals
from spine.L4_runtime.sandbox.simulation_engine import simulate_change

def compute_safe_commit(limit: int = 1000) -> dict:
    proposals = generate_change_proposals(limit=limit)["proposals"]

    safe_commits = []

    for p in proposals:
        sim = simulate_change(p)
        if sim["safe"]:
            safe_commits.append({
                "proposal": p,
                "score": sim["risk_score"]
            })

    return {
        "safe_commit_count": len(safe_commits),
        "safe_commits": safe_commits
    }
PY


# =========================================================
# FILE 4 — CLI V11 (SANDBOX CONTROL CENTER)
# =========================================================
cat > backend/app/spine/L5_api/repo_intelligence_v11_cli.py <<'PY'
from __future__ import annotations

import json

from spine.L4_runtime.repo_intelligence_engine import build_repo_intelligence
from spine.L4_runtime.sandbox.simulation_batch_runner import run_sandbox
from spine.L4_runtime.sandbox.safe_commit_planner import compute_safe_commit

def run(limit: int = 1000):
    report = {
        "repo_intelligence": build_repo_intelligence(limit=limit),

        # SANDBOX LAYER
        "sandbox_results": run_sandbox(limit=limit),
        "safe_commit_plan": compute_safe_commit(limit=limit),
    }

    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    run()
PY


# =========================================================
# FILE 5 — PHASE 11 TESTS
# =========================================================
cat > backend/app/spine/L7_tests/test_phase11_sandbox.py <<'PY'
from spine.L4_runtime.sandbox.simulation_engine import simulate_change
from spine.L4_runtime.sandbox.simulation_batch_runner import run_sandbox
from spine.L4_runtime.sandbox.safe_commit_planner import compute_safe_commit

def test_simulation_engine_runs():
    r = simulate_change({"stack": "risk", "target": "limits"})
    assert "risk_score" in r
    assert "safe" in r

def test_sandbox_batch_runner():
    r = run_sandbox(limit=200)
    assert "total" in r

def test_safe_commit_planner():
    r = compute_safe_commit(limit=200)
    assert "safe_commit_count" in r
PY


# =========================================================
# EXECUTION
# =========================================================

echo "🧠 Running Phase 11 CLI..."
PYTHONPATH=backend/app python3 backend/app/spine/L5_api/repo_intelligence_v11_cli.py

echo "🧪 Running Phase 11 tests..."
PYTHONPATH=backend/app pytest -q backend/app/spine/L7_tests/test_phase11_sandbox.py

echo "✅ Phase 11 Complete"
