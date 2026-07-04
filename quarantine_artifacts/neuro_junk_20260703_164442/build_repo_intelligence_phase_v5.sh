#!/bin/bash
set -e

echo "🧠 Building Repo Intelligence Phase V5 (Architecture Repair + Self-Healing Layer)..."

mkdir -p backend/app/spine/L4_runtime
mkdir -p backend/app/spine/L5_api
mkdir -p backend/app/spine/L7_tests

# =========================================================
# FILE 1 — ARCHITECTURE REPAIR ENGINE (L4)
# =========================================================
cat > backend/app/spine/L4_runtime/architecture_repair_engine.py <<'PY'
from __future__ import annotations

from spine.L4_runtime.repo_intelligence_engine import build_repo_intelligence
from spine.L4_runtime.stack_gap_analyzer import analyze_stack_gaps
from spine.L4_runtime.dependency_graph_engine import build_dependency_graph

def detect_repair_actions(limit: int = 1000) -> dict:
    intel = build_repo_intelligence(limit=limit)
    gaps = analyze_stack_gaps(limit=limit)
    deps = build_dependency_graph(limit=limit)

    repairs = []

    # ---------------------------------------------------------
    # 1. Missing critical stack components
    # ---------------------------------------------------------
    for stack, missing in gaps["gaps"].items():
        for item in missing:
            repairs.append({
                "type": "MISSING_COMPONENT",
                "stack": stack,
                "target": item,
                "action": f"CREATE backend/app/stacks/{stack}/{item}.py"
            })

    # ---------------------------------------------------------
    # 2. Broken dependency chains
    # ---------------------------------------------------------
    for stack, missing_deps in deps["missing_links"].items():
        for dep in missing_deps:
            repairs.append({
                "type": "BROKEN_DEPENDENCY",
                "stack": stack,
                "target": dep,
                "action": f"REVIEW dependency: {stack} -> {dep}"
            })

    # ---------------------------------------------------------
    # 3. Orphan stacks (structural drift)
    # ---------------------------------------------------------
    for orphan in deps.get("missing_links", {}):
        if orphan not in intel["structure"]:
            repairs.append({
                "type": "ORPHAN_STACK",
                "stack": orphan,
                "target": None,
                "action": "REVIEW stack placement or merge candidate"
            })

    return {
        "repairs": repairs,
        "repair_count": len(repairs)
    }

if __name__ == "__main__":
    import json
    print(json.dumps(detect_repair_actions(), indent=2))
PY


# =========================================================
# FILE 2 — STACK REBALANCER (L4)
# =========================================================
cat > backend/app/spine/L4_runtime/stack_rebalancer.py <<'PY'
from __future__ import annotations

from spine.L4_runtime.repo_intelligence_engine import build_repo_intelligence

# Lightweight heuristic rebalance rules
REBALANCE_RULES = {
    "execution": ["broker", "executor"],
    "risk": ["kill_switch", "limits"],
    "strategy": ["selector", "signal"],
    "auth_identity": ["gate", "auth"],
}

def compute_rebalance_actions(limit: int = 1000) -> dict:
    intel = build_repo_intelligence(limit=limit)
    structure = intel["structure"]

    actions = []

    for stack, keywords in REBALANCE_RULES.items():
        files = structure.get(stack, [])

        for kw in keywords:
            if not any(kw in f.lower() for f in files):
                actions.append({
                    "type": "MISSING_WITHIN_STACK",
                    "stack": stack,
                    "missing": kw,
                    "action": f"CREATE/RELOCATE {kw} into {stack}"
                })

    return {
        "rebalance_actions": actions,
        "count": len(actions)
    }

if __name__ == "__main__":
    import json
    print(json.dumps(compute_rebalance_actions(), indent=2))
PY


# =========================================================
# FILE 3 — ARCHITECTURE DIFF ENGINE (L4)
# =========================================================
cat > backend/app/spine/L4_runtime/architecture_diff_engine.py <<'PY'
from __future__ import annotations

from spine.L4_runtime.repo_intelligence_engine import build_repo_intelligence
from spine.L4_runtime.dependency_graph_engine import build_dependency_graph
from spine.L4_runtime.stack_gap_analyzer import analyze_stack_gaps

def compute_architecture_diff(limit: int = 1000) -> dict:
    intel = build_repo_intelligence(limit=limit)
    gaps = analyze_stack_gaps(limit=limit)
    deps = build_dependency_graph(limit=limit)

    diff = {
        "missing_components": gaps["gaps"],
        "broken_dependencies": deps["missing_links"],
        "orphan_stacks": []
    }

    for stack, files in intel["structure"].items():
        if not files and stack not in ["unknown"]:
            diff["orphan_stacks"].append(stack)

    return diff

if __name__ == "__main__":
    import json
    print(json.dumps(compute_architecture_diff(), indent=2))
PY


# =========================================================
# FILE 4 — CLI V5 (SELF-HEALING ENGINE)
# =========================================================
cat > backend/app/spine/L5_api/repo_intelligence_v5_cli.py <<'PY'
from __future__ import annotations

import json

from spine.L4_runtime.repo_intelligence_engine import build_repo_intelligence
from spine.L4_runtime.stack_gap_analyzer import analyze_stack_gaps
from spine.L4_runtime.dependency_graph_engine import build_dependency_graph
from spine.L4_runtime.runtime_wiring_validator import validate_runtime_wiring
from spine.L4_runtime.implementation_planner_v4 import compute_next_implementation
from spine.L4_runtime.architecture_repair_engine import detect_repair_actions
from spine.L4_runtime.stack_rebalancer import compute_rebalance_actions
from spine.L4_runtime.architecture_diff_engine import compute_architecture_diff

def run(limit: int = 1000):
    report = {
        "repo_intelligence": build_repo_intelligence(limit=limit),
        "stack_gaps": analyze_stack_gaps(limit=limit),
        "dependency_graph": build_dependency_graph(limit=limit),
        "wiring_validation": validate_runtime_wiring(limit=limit),
        "next_action": compute_next_implementation(limit=limit),

        # 🔥 NEW SELF-HEALING LAYER
        "repair_actions": detect_repair_actions(limit=limit),
        "rebalance_actions": compute_rebalance_actions(limit=limit),
        "architecture_diff": compute_architecture_diff(limit=limit),
    }

    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    run()
PY


# =========================================================
# FILE 5 — PHASE 5 TESTS (L7)
# =========================================================
cat > backend/app/spine/L7_tests/test_phase5_self_healing.py <<'PY'
from spine.L4_runtime.architecture_repair_engine import detect_repair_actions
from spine.L4_runtime.stack_rebalancer import compute_rebalance_actions
from spine.L4_runtime.architecture_diff_engine import compute_architecture_diff

def test_repair_engine_runs():
    r = detect_repair_actions(limit=200)
    assert "repairs" in r

def test_rebalancer_runs():
    r = compute_rebalance_actions(limit=200)
    assert "rebalance_actions" in r

def test_diff_engine_runs():
    d = compute_architecture_diff(limit=200)
    assert "missing_components" in d
    assert "broken_dependencies" in d
PY


# =========================================================
# EXECUTION
# =========================================================

echo "🧠 Running Phase 5 CLI..."
PYTHONPATH=backend/app python3 backend/app/spine/L5_api/repo_intelligence_v5_cli.py

echo "🧪 Running Phase 5 tests..."
PYTHONPATH=backend/app pytest -q backend/app/spine/L7_tests/test_phase5_self_healing.py

echo "✅ Repo Intelligence Phase V5 Complete"
