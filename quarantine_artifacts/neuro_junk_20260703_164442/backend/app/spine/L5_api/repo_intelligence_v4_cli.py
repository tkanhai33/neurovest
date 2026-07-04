from __future__ import annotations

import json

from spine.L4_runtime.repo_intelligence_engine import build_repo_intelligence
from spine.L4_runtime.stack_gap_analyzer import analyze_stack_gaps
from spine.L4_runtime.dependency_graph_engine import build_dependency_graph
from spine.L4_runtime.runtime_wiring_validator import validate_runtime_wiring
from spine.L4_runtime.implementation_planner_v4 import compute_next_implementation

def run(limit: int = 1000):
    report = {
        "repo_intelligence": build_repo_intelligence(limit=limit),
        "stack_gaps": analyze_stack_gaps(limit=limit),
        "dependency_graph": build_dependency_graph(limit=limit),
        "wiring_validation": validate_runtime_wiring(limit=limit),
        "next_action": compute_next_implementation(limit=limit),
    }

    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    run()
