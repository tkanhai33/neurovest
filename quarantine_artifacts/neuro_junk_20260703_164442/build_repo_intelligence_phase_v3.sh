#!/bin/bash
set -e

echo "🧠 Building Repo Intelligence Phase V3 (Scaffold Generation Layer)..."

mkdir -p backend/app/spine/L4_runtime
mkdir -p backend/app/spine/L2_domain
mkdir -p backend/app/spine/L5_api
mkdir -p backend/app/spine/L7_tests

# =========================================================
# FILE 1 — STACK SCAFFOLD GENERATOR (L4)
# =========================================================
cat > backend/app/spine/L4_runtime/stack_scaffold_generator.py <<'PY'
from __future__ import annotations

from spine.L2_domain.repo_intelligence.repo_scanner import find_repo_root
from spine.L4_runtime.repo_intelligence_engine import build_repo_intelligence
from spine.L4_runtime.stack_gap_analyzer import analyze_stack_gaps
from spine.L2_domain.architecture_contracts import get_contract

def generate_scaffold(stack: str, missing_items: list[str]) -> dict:
    """
    Produces a safe, minimal scaffold blueprint for missing stack components.
    No execution logic — only structure.
    """

    contract = get_contract(stack) or {}

    base_path = f"backend/app/stacks/{stack}"

    files = []

    for item in missing_items:
        file_path = f"{base_path}/{item}.py"

        scaffold = f'''"""
AUTO-GENERATED SCAFFOLD
STACK: {stack}
COMPONENT: {item}

DO NOT PLACE BUSINESS LOGIC HERE YET
ONLY STRUCTURAL PLACEHOLDER
"""

def init():
    raise NotImplementedError("Scaffold not implemented: {item}")
'''

        files.append({
            "path": file_path,
            "content": scaffold
        })

    return {
        "stack": stack,
        "generated_files": files,
        "contract_reference": contract
    }


def generate_from_repo(limit: int = 1000) -> dict:
    intel = build_repo_intelligence(limit=limit)
    gaps = analyze_stack_gaps(limit=limit)

    output = []

    for stack, missing in gaps["gaps"].items():
        output.append(generate_scaffold(stack, missing))

    return {
        "root": str(find_repo_root()),
        "scaffolds": output
    }


if __name__ == "__main__":
    import json
    print(json.dumps(generate_from_repo(), indent=2))
PY


# =========================================================
# FILE 2 — UPDATED NEXT FILE PLANNER (L4 upgrade)
# =========================================================
cat > backend/app/spine/L4_runtime/next_file_planner_v2.py <<'PY'
from __future__ import annotations

from spine.L4_runtime.repo_intelligence_engine import build_repo_intelligence
from spine.L4_runtime.stack_gap_analyzer import analyze_stack_gaps

def compute_next_file(limit: int = 1000) -> dict:
    intel = build_repo_intelligence(limit=limit)
    gaps = analyze_stack_gaps(limit=limit)

    worst_stack = None
    worst_missing = []

    for stack, missing in gaps["gaps"].items():
        if len(missing) > len(worst_missing):
            worst_stack = stack
            worst_missing = missing

    if not worst_stack:
        return {
            "next_file": None,
            "reason": "All stacks complete"
        }

    next_item = worst_missing[0]

    return {
        "next_stack": worst_stack,
        "next_file": f"backend/app/stacks/{worst_stack}/{next_item}.py",
        "reason": f"Missing core component '{next_item}' in {worst_stack}",
        "confidence": "high" if len(worst_missing) > 1 else "medium"
    }
PY


# =========================================================
# FILE 3 — CLI V3 BRIDGE (L5)
# =========================================================
cat > backend/app/spine/L5_api/repo_intelligence_v3_cli.py <<'PY'
from __future__ import annotations

import json

from spine.L4_runtime.repo_intelligence_engine import build_repo_intelligence
from spine.L4_runtime.stack_gap_analyzer import analyze_stack_gaps
from spine.L4_runtime.next_file_planner_v2 import compute_next_file
from spine.L4_runtime.stack_scaffold_generator import generate_from_repo

def run(limit: int = 1000):
    report = {
        "repo_intelligence": build_repo_intelligence(limit=limit),
        "stack_gaps": analyze_stack_gaps(limit=limit),
        "next_action": compute_next_file(limit=limit),
        "scaffolds": generate_from_repo(limit=limit),
    }

    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    run()
PY


# =========================================================
# FILE 4 — L2 CONTRACT EXTENSION (optional reinforcement)
# =========================================================
cat > backend/app/spine/L2_domain/architecture_contracts_v2.py <<'PY'
ARCHITECTURE_CONTRACTS_V2 = {
    "auth_identity": {
        "required": ["gate", "base", "validator"]
    },
    "market_data": {
        "required": ["feed", "bars", "price"]
    },
    "snaptrade": {
        "required": ["adapter", "execution", "broker"]
    },
    "strategy": {
        "required": ["engine", "selector", "signal"]
    },
    "risk": {
        "required": ["limits", "kill_switch", "exposure"]
    },
    "execution": {
        "required": ["sandbox", "broker", "executor"]
    },
    "portfolio": {
        "required": ["allocator", "rebalance"]
    },
    "journal_ledger": {
        "required": ["ledger", "record"]
    },
    "wolfden_ai": {
        "required": ["orchestrator", "routing"]
    }
}
PY


# =========================================================
# FILE 5 — TESTS FOR SCAFFOLD LAYER (L7)
# =========================================================
cat > backend/app/spine/L7_tests/test_stack_scaffolds.py <<'PY'
from spine.L4_runtime.stack_scaffold_generator import generate_from_repo

def test_scaffold_generation_runs():
    result = generate_from_repo(limit=200)
    assert "scaffolds" in result
    assert isinstance(result["scaffolds"], list)

def test_scaffold_structure():
    result = generate_from_repo(limit=200)
    if result["scaffolds"]:
        first = result["scaffolds"][0]
        assert "generated_files" in first
        assert "stack" in first
PY


# =========================================================
# EXECUTION
# =========================================================

echo "🧠 Running V3 CLI..."
PYTHONPATH=backend/app python3 backend/app/spine/L5_api/repo_intelligence_v3_cli.py

echo "🧪 Running tests..."
PYTHONPATH=backend/app pytest -q backend/app/spine/L7_tests/test_stack_scaffolds.py

echo "✅ Repo Intelligence Phase V3 Complete"
