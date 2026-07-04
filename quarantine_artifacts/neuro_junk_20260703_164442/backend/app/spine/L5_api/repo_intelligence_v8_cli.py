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
