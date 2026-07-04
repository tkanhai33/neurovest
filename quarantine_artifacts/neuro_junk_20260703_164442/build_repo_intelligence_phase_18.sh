#!/bin/bash
set -e

echo "🧠 Phase 18 — Contract-Aware Intelligence Orchestrator"

mkdir -p backend/app/spine/L4_runtime/orchestrator
mkdir -p backend/app/spine/L5_api
mkdir -p backend/app/spine/L7_tests


# =========================================================
# FILE 1 — CONTRACT AWARE ANALYZER
# =========================================================
cat > backend/app/spine/L4_runtime/orchestrator/contract_aware_analyzer.py <<'PY'
from __future__ import annotations

from spine.L4_runtime.behavior.behavior_analyzer import analyze_behavior
from spine.L2_domain.architecture_contracts_v2 import ARCHITECTURE_CONTRACTS_V2

def analyze_contract_alignment(limit: int = 1000) -> dict:
    behavior = analyze_behavior(limit=limit)

    misaligned = []

    for stack in behavior["overloaded_stacks"]:
        contract = ARCHITECTURE_CONTRACTS_V2.get(stack, {})

        required = contract.get("required", [])
        layer = contract.get("layer", "UNKNOWN")

        misaligned.append({
            "stack": stack,
            "issue": "OVERLOADED_STACK",
            "expected_layer": layer,
            "expected_components": required,
            "severity": "high"
        })

    for stack in behavior["low_activity_stacks"]:
        contract = ARCHITECTURE_CONTRACTS_V2.get(stack, {})

        misaligned.append({
            "stack": stack,
            "issue": "UNDERUTILIZED_STACK",
            "expected_layer": contract.get("layer", "UNKNOWN"),
            "severity": "medium"
        })

    return {
        "misaligned_stacks": misaligned
    }
PY


# =========================================================
# FILE 2 — INTELLIGENT ROADMAP ENGINE
# =========================================================
cat > backend/app/spine/L4_runtime/orchestrator/intelligent_roadmap_engine.py <<'PY'
from __future__ import annotations

from spine.L4_runtime.behavior.behavior_roadmap_engine import generate_behavior_roadmap
from spine.L4_runtime.orchestrator.contract_aware_analyzer import analyze_contract_alignment

def generate_intelligent_roadmap(limit: int = 1000) -> dict:
    behavior = generate_behavior_roadmap(limit=limit)
    contract = analyze_contract_alignment(limit=limit)

    roadmap = []

    # PRIORITY 1 — CONTRACT VIOLATIONS
    for m in contract["misaligned_stacks"]:
        roadmap.append({
            "stack": m["stack"],
            "action": "REFACTOR_TO_CONTRACT",
            "reason": m["issue"],
            "priority": 3,
            "layer": m["expected_layer"]
        })

    # PRIORITY 2 — BEHAVIOR ISSUES
    for item in behavior.get("roadmap", []):
        roadmap.append({
            "stack": item["stack"],
            "action": item["action"],
            "priority": item["priority"],
            "layer": "behavioral"
        })

    roadmap = sorted(roadmap, key=lambda x: x["priority"], reverse=True)

    if not roadmap:
        return {
            "next": {
                "stack": "system",
                "action": "FULL_CONVERGENCE",
                "priority": 0
            },
            "message": "System is fully aligned with contracts + behavior"
        }

    return {
        "next": roadmap[0],
        "roadmap": roadmap[:10]
    }
PY


# =========================================================
# FILE 3 — CLI
# =========================================================
cat > backend/app/spine/L5_api/repo_intelligence_v18_cli.py <<'PY'
from __future__ import annotations

import json

from spine.L4_runtime.orchestrator.intelligent_roadmap_engine import generate_intelligent_roadmap

def run():
    print(json.dumps(generate_intelligent_roadmap(), indent=2))

if __name__ == "__main__":
    run()
PY


# =========================================================
# FILE 4 — TESTS
# =========================================================
cat > backend/app/spine/L7_tests/test_phase18_orchestrator.py <<'PY'
from spine.L4_runtime.orchestrator.intelligent_roadmap_engine import generate_intelligent_roadmap

def test_intelligent_roadmap():
    r = generate_intelligent_roadmap(limit=200)
    assert "next" in r or "message" in r
PY


# =========================================================
# EXECUTION
# =========================================================

echo "🧠 Running Phase 18 CLI..."
PYTHONPATH=backend/app python3 backend/app/spine/L5_api/repo_intelligence_v18_cli.py

echo "🧪 Running Phase 18 tests..."
PYTHONPATH=backend/app pytest -q backend/app/spine/L7_tests/test_phase18_orchestrator.py

echo "✅ Phase 18 Complete"
