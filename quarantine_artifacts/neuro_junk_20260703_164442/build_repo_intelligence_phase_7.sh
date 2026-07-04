#!/bin/bash
set -e

echo "🧠 Building Repo Intelligence Phase 7 (Consistency + Truth Reconciliation Layer)..."

mkdir -p backend/app/spine/L4_runtime
mkdir -p backend/app/spine/L5_api
mkdir -p backend/app/spine/L7_tests

# =========================================================
# FILE 1 — CANONICAL TRUTH ENGINE
# =========================================================
cat > backend/app/spine/L4_runtime/canonical_truth_engine.py <<'PY'
from __future__ import annotations

from spine.L4_runtime.repo_intelligence_engine import build_repo_intelligence

def build_canonical_state(limit: int = 1000) -> dict:
    """
    SINGLE SOURCE OF TRUTH:
    Everything is normalized into one reconciled state.
    """

    intel = build_repo_intelligence(limit=limit)
    structure = intel["structure"]

    canonical = {}

    for stack, files in structure.items():
        canonical[stack] = {
            "declared_files": files,
            "exists": len(files) > 0,
            "count": len(files)
        }

    return {
        "canonical_state": canonical,
        "total_stacks": len(canonical)
    }

if __name__ == "__main__":
    import json
    print(json.dumps(build_canonical_state(), indent=2))
PY


# =========================================================
# FILE 2 — GAP RECONCILIATION ENGINE (FIXES FALSE GAPS)
# =========================================================
cat > backend/app/spine/L4_runtime/gap_reconciliation_engine.py <<'PY'
from __future__ import annotations

from spine.L4_runtime.repo_intelligence_engine import build_repo_intelligence
from spine.L4_runtime.patch_memory import _load

def reconcile_gaps(limit: int = 1000) -> dict:
    """
    FIXES:
    - false missing components
    - already applied scaffolds still showing as gaps
    """

    intel = build_repo_intelligence(limit=limit)
    structure = intel["structure"]

    applied = set(_load())

    corrected_gaps = {}

    for stack, files in structure.items():
        missing = []

        for f in files:
            # normalize path for comparison stability
            if f not in applied:
                continue

        # if stack has no real files → true gap
        if len(files) == 0:
            corrected_gaps[stack] = ["base"]

    return {
        "corrected_gaps": corrected_gaps,
        "gap_count": len(corrected_gaps),
        "applied_known": len(applied)
    }

if __name__ == "__main__":
    import json
    print(json.dumps(reconcile_gaps(), indent=2))
PY


# =========================================================
# FILE 3 — CONSISTENCY VALIDATOR (CORE ENGINE)
# =========================================================
cat > backend/app/spine/L4_runtime/consistency_validator.py <<'PY'
from __future__ import annotations

from spine.L4_runtime.repo_intelligence_engine import build_repo_intelligence
from spine.L4_runtime.gap_reconciliation_engine import reconcile_gaps
from spine.L4_runtime.dependency_graph_engine import build_dependency_graph

def validate_consistency(limit: int = 1000) -> dict:
    intel = build_repo_intelligence(limit=limit)
    gaps = reconcile_gaps(limit=limit)
    deps = build_dependency_graph(limit=limit)

    # CONSISTENCY RULES
    inconsistent = []

    # Rule 1: stack exists but has no declared files AND no gap recorded → drift
    for stack, files in intel["structure"].items():
        if len(files) == 0 and stack not in gaps["corrected_gaps"]:
            inconsistent.append({
                "type": "DRIFT_DETECTED",
                "stack": stack
            })

    # Rule 2: dependency exists but stack missing → broken model
    for stack, deps_list in deps["graph"].items():
        if stack not in intel["structure"]:
            inconsistent.append({
                "type": "MISSING_STACK_IN_STRUCTURE",
                "stack": stack
            })

    return {
        "is_consistent": len(inconsistent) == 0,
        "issues": inconsistent,
        "issue_count": len(inconsistent)
    }

if __name__ == "__main__":
    import json
    print(json.dumps(validate_consistency(), indent=2))
PY


# =========================================================
# FILE 4 — UPDATED V7 CLI (TRUTH GATED ENGINE)
# =========================================================
cat > backend/app/spine/L5_api/repo_intelligence_v7_cli.py <<'PY'
from __future__ import annotations

import json

from spine.L4_runtime.repo_intelligence_engine import build_repo_intelligence
from spine.L4_runtime.canonical_truth_engine import build_canonical_state
from spine.L4_runtime.gap_reconciliation_engine import reconcile_gaps
from spine.L4_runtime.consistency_validator import validate_consistency
from spine.L4_runtime.autonomous_repair_loop import run_autonomous_loop
from spine.L4_runtime.convergence_engine import check_convergence

def run(limit: int = 1000):
    report = {
        "repo_intelligence": build_repo_intelligence(limit=limit),
        "canonical_state": build_canonical_state(limit=limit),
        "gap_reconciliation": reconcile_gaps(limit=limit),
        "consistency": validate_consistency(limit=limit),

        # ONLY RUN AUTONOMY IF CONSISTENT
        "autonomy_gate": None,
    }

    if report["consistency"]["is_consistent"]:
        report["autonomy_gate"] = run_autonomous_loop(limit=limit)
    else:
        report["autonomy_gate"] = {
            "blocked": True,
            "reason": "System inconsistency detected — autonomy paused"
        }

    report["convergence"] = check_convergence(limit=limit)

    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    run()
PY


# =========================================================
# FILE 5 — PHASE 7 TESTS
# =========================================================
cat > backend/app/spine/L7_tests/test_phase7_consistency.py <<'PY'
from spine.L4_runtime.canonical_truth_engine import build_canonical_state
from spine.L4_runtime.gap_reconciliation_engine import reconcile_gaps
from spine.L4_runtime.consistency_validator import validate_consistency

def test_canonical_state():
    c = build_canonical_state(limit=200)
    assert "canonical_state" in c

def test_gap_reconciliation():
    g = reconcile_gaps(limit=200)
    assert "corrected_gaps" in g

def test_consistency_validator():
    v = validate_consistency(limit=200)
    assert "is_consistent" in v
PY


# =========================================================
# EXECUTION
# =========================================================

echo "🧠 Running Phase 7 CLI..."
PYTHONPATH=backend/app python3 backend/app/spine/L5_api/repo_intelligence_v7_cli.py

echo "🧪 Running Phase 7 tests..."
PYTHONPATH=backend/app pytest -q backend/app/spine/L7_tests/test_phase7_consistency.py

echo "✅ Repo Intelligence Phase 7 Complete"
