#!/bin/bash
set -e

echo "🧠 Phase 8 — Refactor Intelligence + Stack Truth Fix"

mkdir -p backend/app/spine/L4_runtime
mkdir -p backend/app/spine/L5_api
mkdir -p backend/app/spine/L7_tests

cat > backend/app/spine/L4_runtime/repo_intelligence_engine.py <<'PY'
from __future__ import annotations

import json
from spine.L2_domain.repo_intelligence.repo_scanner import find_repo_root, scan_repo

CANONICAL_STACKS = [
    "auth_identity", "market_data", "snaptrade", "strategy", "risk",
    "portfolio", "journal_ledger", "learning_research", "execution",
    "notification", "wolfden_ai", "chat_public", "db_model", "unknown",
]

def classify_stack(path: str) -> str:
    lowered = path.lower()

    # hard stack path truth FIRST
    for stack in CANONICAL_STACKS:
        marker = f"backend/app/stacks/{stack}/"
        if marker in lowered:
            return stack

    # spine layer files
    if "/l0_adapters/" in lowered:
        return "snaptrade" if "broker" in lowered or "snaptrade" in lowered else "unknown"
    if "/l4_runtime/" in lowered and "execution" in lowered:
        return "execution"
    if "neuro" in lowered or "wolfden" in lowered:
        return "wolfden_ai"
    if "market" in lowered:
        return "market_data"
    if "strategy" in lowered:
        return "strategy"
    if "risk" in lowered:
        return "risk"
    if "portfolio" in lowered:
        return "portfolio"
    if "journal" in lowered or "ledger" in lowered:
        return "journal_ledger"
    if "auth" in lowered or "identity" in lowered or "gate" in lowered:
        return "auth_identity"
    if "snaptrade" in lowered or "broker_adapter" in lowered:
        return "snaptrade"
    if "chat" in lowered:
        return "chat_public"

    return "unknown"

def build_repo_intelligence(limit: int = 1000) -> dict:
    root = find_repo_root()
    files = scan_repo(root, limit=limit)
    structure = {stack: [] for stack in CANONICAL_STACKS}

    for file_path in files:
        stack = classify_stack(file_path)
        structure.setdefault(stack, []).append(file_path)

    return {
        "root": str(root),
        "file_count": len(files),
        "summary": {stack: len(paths) for stack, paths in structure.items()},
        "structure": structure,
    }

if __name__ == "__main__":
    print(json.dumps(build_repo_intelligence(), indent=2))
PY

cat > backend/app/spine/L4_runtime/refactor_manifest_engine.py <<'PY'
from __future__ import annotations

from spine.L4_runtime.repo_intelligence_engine import build_repo_intelligence

def build_refactor_manifest(limit: int = 1000) -> dict:
    intel = build_repo_intelligence(limit=limit)
    unknown = intel["structure"].get("unknown", [])

    proposals = []

    for path in unknown:
        if "snapshots/" in path:
            proposals.append({
                "type": "QUARANTINE_CANDIDATE",
                "path": path,
                "reason": "snapshot artifact should not influence active architecture"
            })
        elif "/patches/" in path or "applied_patches" in path:
            proposals.append({
                "type": "AUDIT_ARTIFACT",
                "path": path,
                "reason": "generated patch/audit state, not runtime source"
            })
        elif "/spine/l" in path.lower():
            proposals.append({
                "type": "SPINE_LAYER_FILE",
                "path": path,
                "reason": "valid spine control-plane file, not stack-owned"
            })

    return {
        "proposal_count": len(proposals),
        "proposals": proposals,
        "safe_to_apply": False
    }

if __name__ == "__main__":
    import json
    print(json.dumps(build_refactor_manifest(), indent=2))
PY

cat > backend/app/spine/L5_api/repo_intelligence_v8_cli.py <<'PY'
from __future__ import annotations

import json

from spine.L4_runtime.repo_intelligence_engine import build_repo_intelligence
from spine.L4_runtime.stack_gap_analyzer import analyze_stack_gaps
from spine.L4_runtime.convergence_engine import check_convergence
from spine.L4_runtime.refactor_manifest_engine import build_refactor_manifest

def run(limit: int = 1000):
    print(json.dumps({
        "repo_intelligence": build_repo_intelligence(limit=limit),
        "stack_gaps": analyze_stack_gaps(limit=limit),
        "convergence": check_convergence(limit=limit),
        "refactor_manifest": build_refactor_manifest(limit=limit),
    }, indent=2))

if __name__ == "__main__":
    run()
PY

cat > backend/app/spine/L7_tests/test_phase8_refactor_truth.py <<'PY'
from spine.L4_runtime.repo_intelligence_engine import classify_stack, build_repo_intelligence
from spine.L4_runtime.refactor_manifest_engine import build_refactor_manifest

def test_execution_broker_classifies_as_execution():
    assert classify_stack("backend/app/stacks/execution/broker.py") == "execution"

def test_stack_path_wins_before_keyword():
    assert classify_stack("backend/app/stacks/execution/broker.py") != "snaptrade"

def test_phase8_intelligence_runs():
    data = build_repo_intelligence(limit=300)
    assert "execution" in data["structure"]

def test_refactor_manifest_is_manifest_only():
    m = build_refactor_manifest(limit=300)
    assert m["safe_to_apply"] is False
PY

echo "🧠 Running Phase 8 CLI..."
PYTHONPATH=backend/app python3 backend/app/spine/L5_api/repo_intelligence_v8_cli.py

echo "🧪 Running Phase 8 tests..."
PYTHONPATH=backend/app pytest -q backend/app/spine/L7_tests/test_phase8_refactor_truth.py

echo "✅ Phase 8 Complete"
