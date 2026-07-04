#!/bin/bash
set -e

echo "🧠 Phase 20 — Dependency-Safe Build Compiler"

mkdir -p backend/app/spine/L4_runtime/compiler
mkdir -p backend/app/spine/L5_api
mkdir -p backend/app/spine/L7_tests


# =========================================================
# FILE 1 — BUILD ORDER ENGINE
# =========================================================
cat > backend/app/spine/L4_runtime/compiler/build_order_engine.py <<'PY'
from __future__ import annotations

from spine.L4_runtime.dependency_graph_engine import build_dependency_graph
from spine.L4_runtime.stack_gap_analyzer import analyze_stack_gaps

def compute_build_order(limit: int = 1000) -> dict:
    deps = build_dependency_graph(limit=limit)
    gaps = analyze_stack_gaps(limit=limit)

    graph = deps["graph"]
    missing = gaps["gaps"]

    build_sequence = []
    visited = set()

    def can_build(stack: str) -> bool:
        for dep in graph.get(stack, []):
            if dep in missing and missing.get(dep):
                return False
        return True

    # naive deterministic ordering pass
    for stack in graph:
        if stack in visited:
            continue

        if can_build(stack):
            visited.add(stack)

            items = missing.get(stack, [])
            for item in items:
                build_sequence.append({
                    "stack": stack,
                    "file": item,
                    "reason": "dependency_satisfied",
                    "order": len(build_sequence) + 1
                })

    return {
        "build_sequence": build_sequence,
        "total_steps": len(build_sequence)
    }
PY


# =========================================================
# FILE 2 — EXECUTION COMPILER CLI
# =========================================================
cat > backend/app/spine/L5_api/repo_intelligence_v20_cli.py <<'PY'
from __future__ import annotations

import json

from spine.L4_runtime.compiler.build_order_engine import compute_build_order

def run():
    print(json.dumps(compute_build_order(), indent=2))

if __name__ == "__main__":
    run()
PY


# =========================================================
# FILE 3 — TESTS
# =========================================================
cat > backend/app/spine/L7_tests/test_phase20_compiler.py <<'PY'
from spine.L4_runtime.compiler.build_order_engine import compute_build_order

def test_build_order():
    r = compute_build_order(limit=200)
    assert "build_sequence" in r
PY


# =========================================================
# EXECUTION
# =========================================================

echo "🧠 Running Phase 20 CLI..."
PYTHONPATH=backend/app python3 backend/app/spine/L5_api/repo_intelligence_v20_cli.py

echo "🧪 Running Phase 20 tests..."
PYTHONPATH=backend/app pytest -q backend/app/spine/L7_tests/test_phase20_compiler.py

echo "✅ Phase 20 Complete"
