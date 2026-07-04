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

def recommend_next_file(intel: dict | None = None) -> dict:
    """
    Compatibility shim for older tests.
    Uses the contract patch planner as the current source of truth.
    """
    from spine.L4_runtime.compiler.contract_patch_engine import generate_contract_patch_plan

    plan = generate_contract_patch_plan(limit=1000).get("patch_plan", [])

    if not plan:
        return {
            "next_file": None,
            "reason": "No missing contract files found."
        }

    first = plan[0]
    return {
        "next_file": first.get("file"),
        "reason": first.get("reason", "contract_patch_required")
    }
