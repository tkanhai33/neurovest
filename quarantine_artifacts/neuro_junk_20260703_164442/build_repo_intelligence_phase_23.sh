#!/bin/bash
set -e

echo "🧠 Phase 23 — Execution Staging Compiler"

mkdir -p backend/app/spine/L4_runtime/compiler
mkdir -p backend/app/spine/L5_api
mkdir -p backend/app/spine/L7_tests


# =========================================================
# FILE 1 — DEPENDENCY ORDER ENHANCER
# =========================================================
cat > backend/app/spine/L4_runtime/compiler/execution_order_engine.py <<'PY'
from __future__ import annotations

from collections import defaultdict, deque
from spine.L4_runtime.compiler.contract_diff_engine import compute_contract_diff

def compute_execution_order(limit: int = 1000) -> dict:
    diff = compute_contract_diff(limit=limit)["missing"]

    graph = defaultdict(list)
    indegree = defaultdict(int)

    # build dependency graph (stack-level ordering only)
    for stack in diff:
        for dep in diff:
            if stack != dep:
                graph[dep].append(stack)
                indegree[stack] += 1

    queue = deque([n for n in diff if indegree[n] == 0])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)

        for nxt in graph[node]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)

    return {"order": order}
PY


# =========================================================
# FILE 2 — STAGING ENGINE (NEW CORE)
# =========================================================
cat > backend/app/spine/L4_runtime/compiler/staging_engine.py <<'PY'
from __future__ import annotations

from spine.L4_runtime.compiler.contract_diff_engine import compute_contract_diff
from spine.L4_runtime.compiler.execution_order_engine import compute_execution_order

def build_staged_plan(limit: int = 1000) -> dict:
    diff = compute_contract_diff(limit=limit)["missing"]
    order = compute_execution_order(limit=limit)["order"]

    stages = []
    stage_id = 0

    for stack in order:
        files = diff.get(stack, [])

        if not files:
            continue

        stage_id += 1

        stages.append({
            "stage": stage_id,
            "stack": stack,
            "files": files,
            "risk": "LOW",
            "action": "CREATE_FILES_BATCH"
        })

    return {
        "stages": stages,
        "total_stages": len(stages)
    }
PY


# =========================================================
# FILE 3 — EXECUTION GATE (SAFETY LAYER)
# =========================================================
cat > backend/app/spine/L4_runtime/compiler/execution_gate.py <<'PY'
from __future__ import annotations

def validate_stage(stage: dict) -> dict:
    """
    Prevents unsafe execution batching.
    """

    risk = "LOW"

    if len(stage.get("files", [])) > 5:
        risk = "MEDIUM"

    if stage["stack"] == "execution":
        risk = "HIGH"

    return {
        "approved": risk != "HIGH",
        "risk": risk,
        "stage": stage
    }
PY


# =========================================================
# FILE 4 — CLI
# =========================================================
cat > backend/app/spine/L5_api/repo_intelligence_v23_cli.py <<'PY'
from __future__ import annotations

import json

from spine.L4_runtime.compiler.staging_engine import build_staged_plan
from spine.L4_runtime.compiler.execution_gate import validate_stage

def run():
    plan = build_staged_plan()

    validated = []
    rejected = []

    for stage in plan["stages"]:
        result = validate_stage(stage)

        if result["approved"]:
            validated.append(result)
        else:
            rejected.append(result)

    print(json.dumps({
        "staged_plan": plan,
        "validated": validated,
        "rejected": rejected
    }, indent=2))

if __name__ == "__main__":
    run()
PY


# =========================================================
# FILE 5 — TESTS
# =========================================================
cat > backend/app/spine/L7_tests/test_phase23_staging.py <<'PY'
from spine.L4_runtime.compiler.staging_engine import build_staged_plan
from spine.L4_runtime.compiler.execution_gate import validate_stage

def test_staging():
    r = build_staged_plan(limit=200)
    assert "stages" in r

def test_gate():
    r = validate_stage({"stack": "risk", "files": []})
    assert "approved" in r
PY


# =========================================================
# EXECUTION
# =========================================================

echo "🧠 Running Phase 23 CLI..."
PYTHONPATH=backend/app python3 backend/app/spine/L5_api/repo_intelligence_v23_cli.py

echo "🧪 Running Phase 23 tests..."
PYTHONPATH=backend/app pytest -q backend/app/spine/L7_tests/test_phase23_staging.py

echo "✅ Phase 23 Complete"
