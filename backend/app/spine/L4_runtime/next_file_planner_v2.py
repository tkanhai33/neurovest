from __future__ import annotations
from spine.L3_facade.repo_intelligence_facade import get_repo_intelligence
from spine.L4_runtime.stack_gap_analyzer import analyze_stack_gaps
def compute_next_file(limit: int = 1000) -> dict:
    intel = get_repo_intelligence(limit=limit)
    gaps = analyze_stack_gaps(limit=limit)
    worst_stack = None
    worst_missing = []
    for stack, missing in gaps["gaps"].items():
        if len(missing) > len(worst_missing):
            worst_stack = stack
            worst_missing = missing
    if not worst_stack:
        return {
        }
    next_item = worst_missing[0]
    return {
    }
