from __future__ import annotations
from spine.L3_facade.repo_intelligence_facade import get_repo_intelligence
from spine.L4_runtime.dependency_graph_engine import build_dependency_graph
from spine.L4_runtime.stack_gap_analyzer import analyze_stack_gaps
def compute_architecture_diff(limit: int = 1000) -> dict:
    intel = get_repo_intelligence(limit=limit)
    gaps = analyze_stack_gaps(limit=limit)
    deps = build_dependency_graph(limit=limit)
    diff = {
    }
    for stack, files in intel["structure"].items():
        if not files and stack not in ["unknown"]:
            diff["orphan_stacks"].append(stack)
    return diff
if __name__ == "__main__":
    import json
    print(json.dumps(compute_architecture_diff(), indent=2))
