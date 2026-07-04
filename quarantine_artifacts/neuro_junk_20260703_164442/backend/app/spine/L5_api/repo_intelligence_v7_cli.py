from __future__ import annotations

import json

from spine.L4_runtime.repo_intelligence_engine import build_repo_intelligence
from spine.L4_runtime.canonical_truth_engine import build_canonical_state
from spine.L4_runtime.gap_reconciliation_engine import reconcile_gaps
from spine.L4_runtime.consistency_validator import validate_consistency
from spine.L4_runtime.autonomous_repair_loop import run_autonomous_loop
from spine.L4_runtime.convergence_engine import check_convergence

def run(limit: int = 1000):
    report = {
        "repo_intelligence": build_repo_intelligence(limit=limit),
        "canonical_state": build_canonical_state(limit=limit),
        "gap_reconciliation": reconcile_gaps(limit=limit),
        "consistency": validate_consistency(limit=limit),

        # ONLY RUN AUTONOMY IF CONSISTENT
        "autonomy_gate": None,
    }

    if report["consistency"]["is_consistent"]:
        report["autonomy_gate"] = run_autonomous_loop(limit=limit)
    else:
        report["autonomy_gate"] = {
            "blocked": True,
            "reason": "System inconsistency detected — autonomy paused"
        }

    report["convergence"] = check_convergence(limit=limit)

    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    run()
