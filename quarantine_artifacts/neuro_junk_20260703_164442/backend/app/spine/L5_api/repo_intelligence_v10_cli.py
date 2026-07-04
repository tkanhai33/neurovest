from __future__ import annotations

import json

from spine.L4_runtime.repo_intelligence_engine import build_repo_intelligence
from spine.L4_runtime.convergence_engine import check_convergence
from spine.L4_runtime.governance.change_proposal_engine import generate_change_proposals
from spine.L4_runtime.governance.commit_gate import validate_commit

def run(limit: int = 1000):
    report = {
        "repo_intelligence": build_repo_intelligence(limit=limit),
        "convergence": check_convergence(limit=limit),

        # GOVERNANCE LAYER
        "proposals": generate_change_proposals(limit=limit),
        "commit_gate": validate_commit(limit=limit),
    }

    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    run()
