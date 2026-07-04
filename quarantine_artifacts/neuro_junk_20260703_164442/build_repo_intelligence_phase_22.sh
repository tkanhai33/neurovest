#!/bin/bash
set -e

echo "🧠 Phase 22 — Contract Compiler Core (Deterministic Truth Engine)"

mkdir -p backend/app/spine/L4_runtime/compiler
mkdir -p backend/app/spine/L5_api
mkdir -p backend/app/spine/L7_tests

# =========================================================
# FILE 1 — CONTRACT SPEC COMPILER
# =========================================================
cat > backend/app/spine/L4_runtime/compiler/contract_spec_engine.py <<'PY'
from __future__ import annotations

from spine.L2_domain.architecture_contracts_v2 import ARCHITECTURE_CONTRACTS_V2

BASE = "backend/app/stacks"

def build_contract_spec(limit: int = 1000) -> dict:
    """
    Converts contracts into deterministic file expectations.
    """

    spec = {}

    for stack, contract in ARCHITECTURE_CONTRACTS_V2.items():
        required = contract.get("required", [])

        spec[stack] = [
            f"{BASE}/{stack}/{item}.py"
            for item in required
        ]

    return {"spec": spec}
PY


# =========================================================
# FILE 2 — FILESYSTEM SCANNER (TRUTH LAYER)
# =========================================================
cat > backend/app/spine/L4_runtime/compiler/filesystem_scanner.py <<'PY'
from __future__ import annotations

import os

BASE = "backend/app/stacks"

def scan_filesystem(limit: int = 1000) -> dict:
    """
    Real filesystem truth — NO CONTRACTS involved.
    """

    state = {}

    for stack in os.listdir(BASE):
        stack_path = f"{BASE}/{stack}"
        if not os.path.isdir(stack_path):
            continue

        files = []
        for f in os.listdir(stack_path):
            if f.endswith(".py"):
                files.append(f"{stack_path}/{f}")

        state[stack] = files

    return {"filesystem": state}
PY


# =========================================================
# FILE 3 — CONTRACT DIFF ENGINE (CORE OF PHASE 22)
# =========================================================
cat > backend/app/spine/L4_runtime/compiler/contract_diff_engine.py <<'PY'
from __future__ import annotations

from spine.L4_runtime.compiler.contract_spec_engine import build_contract_spec
from spine.L4_runtime.compiler.filesystem_scanner import scan_filesystem

def compute_contract_diff(limit: int = 1000) -> dict:
    spec = build_contract_spec(limit=limit)["spec"]
    fs = scan_filesystem(limit=limit)["filesystem"]

    missing = {}
    extra = {}

    # -----------------------------
    # MISSING FILES (REAL TRUTH)
    # -----------------------------
    for stack, expected_files in spec.items():
        existing = set(fs.get(stack, []))

        missing_files = [
            f for f in expected_files
            if f not in existing
        ]

        if missing_files:
            missing[stack] = missing_files

    # -----------------------------
    # EXTRA FILES (DRIFT DETECTION)
    # -----------------------------
    for stack, files in fs.items():
        expected = set(spec.get(stack, []))

        extras = [
            f for f in files
            if f not in expected
        ]

        if extras:
            extra[stack] = extras

    return {
        "missing": missing,
        "extra": extra
    }
PY


# =========================================================
# FILE 4 — PATCH PLAN GENERATOR (CLEAN VERSION)
# =========================================================
cat > backend/app/spine/L4_runtime/compiler/contract_patch_engine.py <<'PY'
from __future__ import annotations

from spine.L4_runtime.compiler.contract_diff_engine import compute_contract_diff

def generate_contract_patch_plan(limit: int = 1000) -> dict:
    diff = compute_contract_diff(limit=limit)

    patch_plan = []
    step = 0

    # ONLY TRUE MISSING FILES (NO GUESSING EVER)
    for stack, files in diff["missing"].items():
        for f in files:
            step += 1
            patch_plan.append({
                "step": step,
                "file": f,
                "action": "CREATE_FILE",
                "reason": "contract_spec_missing"
            })

    return {
        "patch_plan": patch_plan,
        "total_steps": len(patch_plan),
        "drift_count": len(diff["extra"])
    }
PY


# =========================================================
# FILE 5 — CLI
# =========================================================
cat > backend/app/spine/L5_api/repo_intelligence_v22_cli.py <<'PY'
from __future__ import annotations

import json

from spine.L4_runtime.compiler.contract_patch_engine import generate_contract_patch_plan
from spine.L4_runtime.compiler.contract_diff_engine import compute_contract_diff

def run():
    report = {
        "diff": compute_contract_diff(),
        "patch_plan": generate_contract_patch_plan()
    }

    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    run()
PY


# =========================================================
# FILE 6 — TESTS
# =========================================================
cat > backend/app/spine/L7_tests/test_phase22_contract_compiler.py <<'PY'
from spine.L4_runtime.compiler.contract_diff_engine import compute_contract_diff
from spine.L4_runtime.compiler.contract_patch_engine import generate_contract_patch_plan

def test_contract_diff():
    r = compute_contract_diff(limit=200)
    assert "missing" in r
    assert "extra" in r

def test_patch_plan():
    r = generate_contract_patch_plan(limit=200)
    assert "patch_plan" in r
    assert "total_steps" in r
PY


# =========================================================
# EXECUTION
# =========================================================

echo "🧠 Running Phase 22 CLI..."
PYTHONPATH=backend/app python3 backend/app/spine/L5_api/repo_intelligence_v22_cli.py

echo "🧪 Running Phase 22 tests..."
PYTHONPATH=backend/app pytest -q backend/app/spine/L7_tests/test_phase22_contract_compiler.py

echo "✅ Phase 22 Complete"
