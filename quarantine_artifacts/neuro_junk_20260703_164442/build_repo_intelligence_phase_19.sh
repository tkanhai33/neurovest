#!/bin/bash
set -e

echo "🧠 Phase 19 — Execution-Grade Roadmap Engine"

mkdir -p backend/app/spine/L4_runtime/roadmap
mkdir -p backend/app/spine/L5_api
mkdir -p backend/app/spine/L7_tests


# =========================================================
# FILE 1 — VALIDATED ROADMAP ENGINE
# =========================================================
cat > backend/app/spine/L4_runtime/roadmap/validated_roadmap_engine.py <<'PY'
from __future__ import annotations

from spine.L4_runtime.behavior.behavior_analyzer import analyze_behavior
from spine.L2_domain.architecture_contracts_v2 import ARCHITECTURE_CONTRACTS_V2

ALLOWED_LAYERS = {
    "auth_identity": "L1_security",
    "strategy": "L2_domain",
    "risk": "L2_domain",
    "execution": "L2_domain",
    "portfolio": "L2_domain",
    "journal_ledger": "L2_domain",
    "market_data": "L0_external",
    "wolfden_ai": "L3_facade"
}

def generate_validated_roadmap(limit: int = 1000) -> dict:
    behavior = analyze_behavior(limit=limit)

    candidates = []

    for stack in behavior["overloaded_stacks"] + behavior["low_activity_stacks"]:

        contract = ARCHITECTURE_CONTRACTS_V2.get(stack)

        if not contract:
            continue

        required = contract.get("required", [])

        for item in required:

            # ❌ filter invalid targets
            if stack == "unknown":
                continue

            layer = ALLOWED_LAYERS.get(stack, "UNKNOWN")

            candidates.append({
                "stack": stack,
                "file": item,
                "layer": layer,
                "priority": len(required)
            })

    # sort best candidate first
    candidates = sorted(candidates, key=lambda x: x["priority"], reverse=True)

    if not candidates:
        return {
            "next_action": None,
            "message": "System is fully compliant"
        }

    return {
        "next_action": candidates[0],
        "roadmap": candidates[:10]
    }
PY


# =========================================================
# FILE 2 — CLI
# =========================================================
cat > backend/app/spine/L5_api/repo_intelligence_v19_cli.py <<'PY'
from __future__ import annotations

import json

from spine.L4_runtime.roadmap.validated_roadmap_engine import generate_validated_roadmap

def run():
    print(json.dumps(generate_validated_roadmap(), indent=2))

if __name__ == "__main__":
    run()
PY


# =========================================================
# FILE 3 — TESTS
# =========================================================
cat > backend/app/spine/L7_tests/test_phase19_roadmap.py <<'PY'
from spine.L4_runtime.roadmap.validated_roadmap_engine import generate_validated_roadmap

def test_validated_roadmap():
    r = generate_validated_roadmap(limit=200)
    assert "next_action" in r or "message" in r
PY


# =========================================================
# EXECUTION
# =========================================================

echo "🧠 Running Phase 19 CLI..."
PYTHONPATH=backend/app python3 backend/app/spine/L5_api/repo_intelligence_v19_cli.py

echo "🧪 Running Phase 19 tests..."
PYTHONPATH=backend/app pytest -q backend/app/spine/L7_tests/test_phase19_roadmap.py

echo "✅ Phase 19 Complete"
