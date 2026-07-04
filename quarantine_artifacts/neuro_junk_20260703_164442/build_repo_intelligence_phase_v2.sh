#!/bin/bash
set -e

echo "🧠 Building Repo Intelligence Phase V2 (contracts + planning layer)..."

mkdir -p backend/app/spine/L2_domain
mkdir -p backend/app/spine/L4_runtime
mkdir -p backend/app/spine/L5_api
mkdir -p backend/app/spine/L7_tests

# =========================================================
# FILE 1 — STACK GAP ANALYZER (L4)
# =========================================================
cat > backend/app/spine/L4_runtime/stack_gap_analyzer.py <<'PY'
from __future__ import annotations

from spine.L4_runtime.repo_intelligence_engine import build_repo_intelligence

REQUIRED_BY_STACK = {
    "auth_identity": ["gate", "base"],
    "market_data": ["base"],
    "snaptrade": ["adapter", "execution"],
    "strategy": ["engine", "selector"],
    "risk": ["limits", "kill_switch"],
    "execution": ["sandbox", "broker"],
    "portfolio": ["allocator"],
    "journal_ledger": ["ledger"],
    "wolfden_ai": ["orchestrator"],
}

def analyze_stack_gaps(limit: int = 1000) -> dict:
    intel = build_repo_intelligence(limit=limit)
    structure = intel["structure"]

    gaps = {}

    for stack, required_keywords in REQUIRED_BY_STACK.items():
        files = structure.get(stack, [])
        missing = []

        for req in required_keywords:
            if not any(req in f.lower() for f in files):
                missing.append(req)

        if missing:
            gaps[stack] = missing

    return {
        "gaps": gaps,
        "total_gaps": sum(len(v) for v in gaps.values())
    }

if __name__ == "__main__":
    import json
    print(json.dumps(analyze_stack_gaps(), indent=2))
PY


# =========================================================
# FILE 2 — ARCHITECTURE CONTRACT REGISTRY (L2)
# =========================================================
cat > backend/app/spine/L2_domain/architecture_contracts.py <<'PY'
ARCHITECTURE_CONTRACTS = {
    "auth_identity": {
        "must_have": ["gate", "auth", "identity"],
    },
    "market_data": {
        "must_have": ["price", "bars", "feed"],
    },
    "snaptrade": {
        "must_have": ["adapter", "execution", "broker"],
    },
    "strategy": {
        "must_have": ["engine", "selector", "signal"],
    },
    "risk": {
        "must_have": ["limits", "exposure", "kill"],
    },
    "execution": {
        "must_have": ["sandbox", "executor"],
    },
    "portfolio": {
        "must_have": ["allocation", "rebalance"],
    },
    "journal_ledger": {
        "must_have": ["ledger", "record"],
    },
    "wolfden_ai": {
        "must_have": ["orchestrator", "routing"],
    }
}

def get_contract(stack: str):
    return ARCHITECTURE_CONTRACTS.get(stack)
PY


# =========================================================
# FILE 3 — NEXT FILE PLANNER (L4)
# =========================================================
cat > backend/app/spine/L4_runtime/next_file_planner.py <<'PY'
from __future__ import annotations

from spine.L4_runtime.repo_intelligence_engine import build_repo_intelligence
from spine.L4_runtime.stack_gap_analyzer import analyze_stack_gaps

def compute_next_file(limit: int = 1000) -> dict:
    intel = build_repo_intelligence(limit=limit)
    gaps = analyze_stack_gaps(limit=limit)

    # pick most broken stack
    worst_stack = None
    worst_count = 0

    for stack, missing in gaps["gaps"].items():
        if len(missing) > worst_count:
            worst_stack = stack
            worst_count = len(missing)

    if not worst_stack:
        return {
            "next_file": None,
            "reason": "All stacks appear structurally complete"
        }

    missing_items = gaps["gaps"][worst_stack]

    suggested_file = f"backend/app/stacks/{worst_stack}/AUTO_GENERATED_{missing_items[0]}.py"

    return {
        "next_file": suggested_file,
        "reason": f"Stack '{worst_stack}' missing {missing_items}",
        "confidence": "high" if worst_count > 1 else "medium"
    }

if __name__ == "__main__":
    import json
    print(json.dumps(compute_next_file(), indent=2))
PY


# =========================================================
# FILE 4 — CLI BRIDGE V2 (L5)
# =========================================================
cat > backend/app/spine/L5_api/repo_intelligence_v2_cli.py <<'PY'
from __future__ import annotations

import json
from spine.L4_runtime.repo_intelligence_engine import build_repo_intelligence
from spine.L4_runtime.stack_gap_analyzer import analyze_stack_gaps
from spine.L4_runtime.next_file_planner import compute_next_file

def run(limit: int = 1000):
    report = {
        "repo_intelligence": build_repo_intelligence(limit=limit),
        "stack_gaps": analyze_stack_gaps(limit=limit),
        "next_action": compute_next_file(limit=limit),
    }

    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    run()
PY


# =========================================================
# FILE 5 — STACK CONTRACT TESTS (L7)
# =========================================================
cat > backend/app/spine/L7_tests/test_stack_contracts.py <<'PY'
from spine.L4_runtime.repo_intelligence_engine import build_repo_intelligence
from spine.L4_runtime.stack_gap_analyzer import analyze_stack_gaps
from spine.L4_runtime.next_file_planner import compute_next_file

def test_repo_intelligence_runs():
    data = build_repo_intelligence(limit=200)
    assert "structure" in data

def test_stack_gap_analyzer_runs():
    gaps = analyze_stack_gaps(limit=200)
    assert "gaps" in gaps

def test_next_file_planner_runs():
    result = compute_next_file(limit=200)
    assert "next_file" in result
    assert "reason" in result
PY


# =========================================================
# EXECUTION
# =========================================================

echo "🧠 Running V2 intelligence CLI..."
PYTHONPATH=backend/app python3 backend/app/spine/L5_api/repo_intelligence_v2_cli.py

echo "🧪 Running tests..."
PYTHONPATH=backend/app pytest -q backend/app/spine/L7_tests/test_stack_contracts.py

echo "✅ Repo Intelligence Phase V2 Complete"
