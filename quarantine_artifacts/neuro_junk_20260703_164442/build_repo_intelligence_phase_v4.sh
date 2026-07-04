#!/bin/bash
set -e

echo "🧠 Building Repo Intelligence Phase V4 (Dependency + Wiring Layer)..."

mkdir -p backend/app/spine/L4_runtime
mkdir -p backend/app/spine/L5_api
mkdir -p backend/app/spine/L7_tests

# =========================================================
# FILE 1 — DEPENDENCY GRAPH ENGINE (L4)
# =========================================================
cat > backend/app/spine/L4_runtime/dependency_graph_engine.py <<'PY'
from __future__ import annotations

from spine.L4_runtime.repo_intelligence_engine import build_repo_intelligence

# Defines logical runtime dependencies between stacks
DEPENDENCY_MAP = {
    "strategy": ["market_data", "risk"],
    "risk": ["execution"],
    "execution": ["snaptrade"],
    "portfolio": ["strategy", "risk"],
    "journal_ledger": ["portfolio", "execution"],
    "wolfden_ai": ["strategy", "risk", "execution"],
    "snaptrade": [],
    "market_data": [],
    "auth_identity": [],
    "chat_public": [],
}

def build_dependency_graph(limit: int = 1000) -> dict:
    intel = build_repo_intelligence(limit=limit)
    structure = intel["structure"]

    graph = {}
    missing_links = {}

    for stack, deps in DEPENDENCY_MAP.items():
        graph[stack] = deps

        missing = []
        for dep in deps:
            if not structure.get(dep):
                missing.append(dep)

        if missing:
            missing_links[stack] = missing

    return {
        "graph": graph,
        "missing_links": missing_links,
        "total_missing_links": sum(len(v) for v in missing_links.values())
    }

if __name__ == "__main__":
    import json
    print(json.dumps(build_dependency_graph(), indent=2))
PY


# =========================================================
# FILE 2 — WIRING VALIDATOR (L4)
# =========================================================
cat > backend/app/spine/L4_runtime/runtime_wiring_validator.py <<'PY'
from __future__ import annotations

from spine.L4_runtime.repo_intelligence_engine import build_repo_intelligence
from spine.L4_runtime.dependency_graph_engine import build_dependency_graph

def validate_runtime_wiring(limit: int = 1000) -> dict:
    intel = build_repo_intelligence(limit=limit)
    deps = build_dependency_graph(limit=limit)

    structure = intel["structure"]

    violations = []

    for stack, missing in deps["missing_links"].items():
        for dep in missing:
            violations.append({
                "stack": stack,
                "missing_dependency": dep,
                "severity": "high"
            })

    # detect orphan stacks (no dependencies but no implementation)
    orphans = []
    for stack, files in structure.items():
        if not files and stack not in ["unknown"]:
            orphans.append(stack)

    return {
        "violations": violations,
        "orphan_stacks": orphans,
        "violation_count": len(violations),
        "orphan_count": len(orphans)
    }

if __name__ == "__main__":
    import json
    print(json.dumps(validate_runtime_wiring(), indent=2))
PY


# =========================================================
# FILE 3 — IMPLEMENTATION PLANNER V4 (L4)
# =========================================================
cat > backend/app/spine/L4_runtime/implementation_planner_v4.py <<'PY'
from __future__ import annotations

from spine.L4_runtime.repo_intelligence_engine import build_repo_intelligence
from spine.L4_runtime.stack_gap_analyzer import analyze_stack_gaps
from spine.L4_runtime.dependency_graph_engine import build_dependency_graph

def compute_next_implementation(limit: int = 1000) -> dict:
    intel = build_repo_intelligence(limit=limit)
    gaps = analyze_stack_gaps(limit=limit)
    deps = build_dependency_graph(limit=limit)

    worst_stack = None
    worst_score = -1

    for stack, missing in gaps["gaps"].items():
        dependency_penalty = len(deps["missing_links"].get(stack, []))
        score = len(missing) + dependency_penalty

        if score > worst_score:
            worst_score = score
            worst_stack = stack

    if not worst_stack:
        return {
            "next_stack": None,
            "next_file": None,
            "reason": "System fully consistent"
        }

    next_missing = gaps["gaps"][worst_stack][0] if gaps["gaps"][worst_stack] else "base"

    return {
        "next_stack": worst_stack,
        "next_file": f"backend/app/stacks/{worst_stack}/{next_missing}.py",
        "reason": "Prioritized by gap + dependency pressure",
        "score": worst_score
    }

if __name__ == "__main__":
    import json
    print(json.dumps(compute_next_implementation(), indent=2))
PY


# =========================================================
# FILE 4 — CLI V4 BRIDGE (L5)
# =========================================================
cat > backend/app/spine/L5_api/repo_intelligence_v4_cli.py <<'PY'
from __future__ import annotations

import json

from spine.L4_runtime.repo_intelligence_engine import build_repo_intelligence
from spine.L4_runtime.stack_gap_analyzer import analyze_stack_gaps
from spine.L4_runtime.dependency_graph_engine import build_dependency_graph
from spine.L4_runtime.runtime_wiring_validator import validate_runtime_wiring
from spine.L4_runtime.implementation_planner_v4 import compute_next_implementation

def run(limit: int = 1000):
    report = {
        "repo_intelligence": build_repo_intelligence(limit=limit),
        "stack_gaps": analyze_stack_gaps(limit=limit),
        "dependency_graph": build_dependency_graph(limit=limit),
        "wiring_validation": validate_runtime_wiring(limit=limit),
        "next_action": compute_next_implementation(limit=limit),
    }

    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    run()
PY


# =========================================================
# FILE 5 — PHASE 4 TESTS (L7)
# =========================================================
cat > backend/app/spine/L7_tests/test_phase4_system.py <<'PY'
from spine.L4_runtime.dependency_graph_engine import build_dependency_graph
from spine.L4_runtime.runtime_wiring_validator import validate_runtime_wiring
from spine.L4_runtime.implementation_planner_v4 import compute_next_implementation

def test_dependency_graph_builds():
    g = build_dependency_graph(limit=200)
    assert "graph" in g
    assert "missing_links" in g

def test_wiring_validator_runs():
    v = validate_runtime_wiring(limit=200)
    assert "violations" in v
    assert "orphan_stacks" in v

def test_implementation_planner_runs():
    p = compute_next_implementation(limit=200)
    assert "next_stack" in p
    assert "next_file" in p
PY


# =========================================================
# EXECUTION
# =========================================================

echo "🧠 Running Phase 4 CLI..."
PYTHONPATH=backend/app python3 backend/app/spine/L5_api/repo_intelligence_v4_cli.py

echo "🧪 Running Phase 4 tests..."
PYTHONPATH=backend/app pytest -q backend/app/spine/L7_tests/test_phase4_system.py

echo "✅ Repo Intelligence Phase V4 Complete"
