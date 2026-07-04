from __future__ import annotations

import json

from spine.L4_runtime.repo_intelligence_engine import build_repo_intelligence
from spine.L4_runtime.stack_gap_analyzer import analyze_stack_gaps
from spine.L4_runtime.next_file_planner_v2 import compute_next_file
from spine.L4_runtime.stack_scaffold_generator import generate_from_repo

def run(limit: int = 1000):
    report = {
        "repo_intelligence": build_repo_intelligence(limit=limit),
        "stack_gaps": analyze_stack_gaps(limit=limit),
        "next_action": compute_next_file(limit=limit),
        "scaffolds": generate_from_repo(limit=limit),
    }

    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    run()
