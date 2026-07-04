from __future__ import annotations
from spine.L3_facade.repo_intelligence_facade import get_repo_intelligence
def analyze_behavior(limit: int = 1000) -> dict:
    intel = get_repo_intelligence(limit=limit)["structure"]
    behavior_report = {
    }
    for stack, files in intel.items():
        # silent = exists but basically unused
        if len(files) == 0:
            behavior_report["silent_stacks"].append(stack)
        # low activity = minimal implementation
        elif len(files) <= 2:
            behavior_report["low_activity_stacks"].append(stack)
        # overloaded = too many responsibilities
        elif len(files) >= 10:
            behavior_report["overloaded_stacks"].append(stack)
    return behavior_report
