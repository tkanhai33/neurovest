from __future__ import annotations
import os
from spine.L2_domain.architecture_contracts_v2 import ARCHITECTURE_CONTRACTS_V2
BASE = "backend/app/stacks"
def compute_reality_gaps(limit: int = 1000) -> dict:
    gaps = {}
    for stack, contract in ARCHITECTURE_CONTRACTS_V2.items():
        required = contract.get("required", [])
        stack_path = f"{BASE}/{stack}"
        existing_files = set()
        if os.path.exists(stack_path):
            for f in os.listdir(stack_path):
                if f.endswith(".py"):
                    existing_files.add(f.replace(".py", ""))
        missing = [r for r in required if r not in existing_files]
        if missing:
            gaps[stack] = missing
    return {
    }
