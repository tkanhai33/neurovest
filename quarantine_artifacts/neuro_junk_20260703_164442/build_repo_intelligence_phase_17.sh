#!/bin/bash
set -e

echo "🧠 Phase 17 — Behavioral Intelligence Layer"

mkdir -p backend/app/spine/L4_runtime/behavior
mkdir -p backend/app/spine/L5_api
mkdir -p backend/app/spine/L7_tests


# =========================================================
# FILE 1 — BEHAVIOR ANALYZER
# =========================================================
cat > backend/app/spine/L4_runtime/behavior/behavior_analyzer.py <<'PY'
from __future__ import annotations

from spine.L4_runtime.repo_intelligence_engine import build_repo_intelligence

def analyze_behavior(limit: int = 1000) -> dict:
    intel = build_repo_intelligence(limit=limit)["structure"]

    behavior_report = {
        "silent_stacks": [],
        "low_activity_stacks": [],
        "overloaded_stacks": []
    }

    for stack, files in intel.items():

        # silent = exists but basically unused
        if len(files) == 0:
            behavior_report["silent_stacks"].append(stack)

        # low activity = minimal implementation
        elif len(files) <= 2:
            behavior_report["low_activity_stacks"].append(stack)

        # overloaded = too many responsibilities
        elif len(files) >= 10:
            behavior_report["overloaded_stacks"].append(stack)

    return behavior_report
PY


# =========================================================
# FILE 2 — BEHAVIORAL ROADMAP ENGINE
# =========================================================
cat > backend/app/spine/L4_runtime/behavior/behavior_roadmap_engine.py <<'PY'
from __future__ import annotations

from spine.L4_runtime.behavior.behavior_analyzer import analyze_behavior

def generate_behavior_roadmap(limit: int = 1000) -> dict:
    behavior = analyze_behavior(limit=limit)

    actions = []

    # silent stacks = highest priority fix
    for s in behavior["silent_stacks"]:
        actions.append({
            "stack": s,
            "action": "ACTIVATE_STACK",
            "priority": 3
        })

    # overloaded stacks = split responsibility
    for s in behavior["overloaded_stacks"]:
        actions.append({
            "stack": s,
            "action": "SPLIT_STACK",
            "priority": 2
        })

    # low activity = expand functionality
    for s in behavior["low_activity_stacks"]:
        actions.append({
            "stack": s,
            "action": "EXPAND_STACK",
            "priority": 1
        })

    actions = sorted(actions, key=lambda x: x["priority"], reverse=True)

    if not actions:
        return {
            "next": {
                "stack": "system",
                "action": "STABLE_BEHAVIOR",
                "priority": 0
            },
            "message": "System behavior is balanced"
        }

    return {
        "next": actions[0],
        "roadmap": actions[:10]
    }
PY


# =========================================================
# FILE 3 — CLI
# =========================================================
cat > backend/app/spine/L5_api/repo_intelligence_v17_cli.py <<'PY'
from __future__ import annotations

import json

from spine.L4_runtime.behavior.behavior_roadmap_engine import generate_behavior_roadmap
from spine.L4_runtime.behavior.behavior_analyzer import analyze_behavior

def run():
    report = {
        "behavior_analysis": analyze_behavior(),
        "roadmap": generate_behavior_roadmap()
    }

    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    run()
PY


# =========================================================
# FILE 4 — TESTS
# =========================================================
cat > backend/app/spine/L7_tests/test_phase17_behavior.py <<'PY'
from spine.L4_runtime.behavior.behavior_analyzer import analyze_behavior
from spine.L4_runtime.behavior.behavior_roadmap_engine import generate_behavior_roadmap

def test_behavior_analyzer():
    r = analyze_behavior(limit=200)
    assert "silent_stacks" in r

def test_behavior_roadmap():
    r = generate_behavior_roadmap(limit=200)
    assert "next" in r or "roadmap" in r
PY


# =========================================================
# EXECUTION
# =========================================================

echo "🧠 Running Phase 17 CLI..."
PYTHONPATH=backend/app python3 backend/app/spine/L5_api/repo_intelligence_v17_cli.py

echo "🧪 Running Phase 17 tests..."
PYTHONPATH=backend/app pytest -q backend/app/spine/L7_tests/test_phase17_behavior.py

echo "✅ Phase 17 Complete"
