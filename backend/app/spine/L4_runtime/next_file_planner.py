from __future__ import annotations
from spine.L3_facade.repo_intelligence_facade import get_repo_intelligence
from spine.L4_runtime.stack_gap_analyzer import analyze_stack_gaps
def compute_next_file(limit: int = 1000) -> dict:
    intel = get_repo_intelligence(limit=limit)
    gaps = analyze_stack_gaps(limit=limit)
    # pick most broken stack
    worst_stack = None
    worst_count = 0
    for stack, missing in gaps["gaps"].items():
        if len(missing) > worst_count:
            worst_stack = stack
            worst_count = len(missing)
    if not worst_stack:
        return {
        }
    missing_items = gaps["gaps"][worst_stack]
    suggested_file = f"backend/app/stacks/{worst_stack}/AUTO_GENERATED_{missing_items[0]}.py"
    return {
    }
if __name__ == "__main__":
    import json
    print(json.dumps(compute_next_file(), indent=2))
