from __future__ import annotations

import json

from spine.L4_runtime.repo_intelligence_engine import build_repo_intelligence
from spine.L4_runtime.sandbox.simulation_batch_runner import run_sandbox
from spine.L4_runtime.sandbox.safe_commit_planner import compute_safe_commit

def run(limit: int = 1000):
    report = {
        "repo_intelligence": build_repo_intelligence(limit=limit),

        # SANDBOX LAYER
        "sandbox_results": run_sandbox(limit=limit),
        "safe_commit_plan": compute_safe_commit(limit=limit),
    }

    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    run()
