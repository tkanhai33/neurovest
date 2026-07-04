#!/bin/bash
set -e

echo "🧠 Building clean repo intelligence phase..."

mkdir -p backend/app/spine/L2_domain/repo_intelligence
mkdir -p backend/app/spine/L3_facade
mkdir -p backend/app/spine/L4_runtime
mkdir -p backend/app/spine/L5_api

touch backend/app/spine/L2_domain/repo_intelligence/__init__.py

cat > backend/app/spine/L4_runtime/repo_intelligence_engine.py <<'PY'
from __future__ import annotations

import json
from pathlib import Path
from spine.L2_domain.repo_intelligence.repo_scanner import find_repo_root, scan_repo

STACK_HINTS = {
    "auth": "auth_identity",
    "identity": "auth_identity",
    "broker": "snaptrade",
    "snaptrade": "snaptrade",
    "execution": "execution",
    "risk": "risk",
    "strategy": "strategy",
    "market": "market_data",
    "chat": "chat_public",
    "ledger": "journal_ledger",
    "journal": "journal_ledger",
    "portfolio": "portfolio",
    "wolfden": "wolfden_ai",
    "neuro": "wolfden_ai",
}

CANONICAL_STACKS = [
    "auth_identity",
    "market_data",
    "snaptrade",
    "strategy",
    "risk",
    "portfolio",
    "journal_ledger",
    "learning_research",
    "execution",
    "notification",
    "wolfden_ai",
    "chat_public",
    "db_model",
    "unknown",
]

def classify_stack(path: str) -> str:
    lowered = path.lower()
    for hint, stack in STACK_HINTS.items():
        if hint in lowered:
            return stack
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

def recommend_next_file(intel: dict | None = None) -> dict:
    intel = intel or build_repo_intelligence()

    required = [
        "backend/app/spine/L2_domain/repo_intelligence/repo_scanner.py",
        "backend/app/spine/L4_runtime/repo_intelligence_engine.py",
        "backend/app/spine/L3_facade/repo_intelligence_facade.py",
        "backend/app/spine/L5_api/repo_intelligence_cli_bridge.py",
        "backend/app/spine/L7_tests/test_repo_intelligence.py",
    ]

    existing = set()
    for paths in intel["structure"].values():
        existing.update(paths)

    for path in required:
        if path not in existing:
            return {
                "next_file": path,
                "reason": "Required repo intelligence pipeline file is missing.",
            }

    return {
        "next_file": None,
        "reason": "Repo intelligence pipeline baseline exists.",
    }

if __name__ == "__main__":
    data = build_repo_intelligence()
    data["recommendation"] = recommend_next_file(data)
    print(json.dumps(data, indent=2))
PY

cat > backend/app/spine/L3_facade/repo_intelligence_facade.py <<'PY'
from __future__ import annotations

from spine.L4_runtime.repo_intelligence_engine import (
    build_repo_intelligence,
    recommend_next_file,
)

def get_repo_architecture_report(limit: int = 1000) -> dict:
    intel = build_repo_intelligence(limit=limit)
    intel["recommendation"] = recommend_next_file(intel)
    return intel
PY

cat > backend/app/spine/L5_api/repo_intelligence_cli_bridge.py <<'PY'
from __future__ import annotations

import json
from spine.L3_facade.repo_intelligence_facade import get_repo_architecture_report

def print_repo_architecture_report(limit: int = 1000) -> None:
    report = get_repo_architecture_report(limit=limit)
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    print_repo_architecture_report()
PY

cat > backend/app/spine/L7_tests/test_repo_intelligence.py <<'PY'
from spine.L2_domain.repo_intelligence.repo_scanner import scan_repo, find_repo_root
from spine.L4_runtime.repo_intelligence_engine import build_repo_intelligence, recommend_next_file
from spine.L3_facade.repo_intelligence_facade import get_repo_architecture_report

def test_repo_scanner_excludes_venv():
    root = find_repo_root()
    files = scan_repo(root, limit=1000)
    assert files
    assert not any(".venv" in path for path in files)
    assert not any("site-packages" in path for path in files)

def test_repo_intelligence_builds_summary():
    intel = build_repo_intelligence(limit=1000)
    assert "summary" in intel
    assert "structure" in intel
    assert "unknown" in intel["structure"]

def test_repo_intelligence_recommends_safely():
    intel = build_repo_intelligence(limit=1000)
    recommendation = recommend_next_file(intel)
    assert "next_file" in recommendation
    assert "reason" in recommendation

def test_repo_intelligence_facade_report():
    report = get_repo_architecture_report(limit=1000)
    assert "recommendation" in report
    assert "summary" in report
PY

echo "✅ Files written."

echo "🧪 Running repo intelligence bridge..."
PYTHONPATH=backend/app python3 backend/app/spine/L5_api/repo_intelligence_cli_bridge.py

echo "🧪 Running tests..."
PYTHONPATH=backend/app pytest -q backend/app/spine/L7_tests/test_repo_intelligence.py
