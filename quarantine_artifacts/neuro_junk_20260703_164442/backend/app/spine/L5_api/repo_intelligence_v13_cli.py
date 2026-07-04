from __future__ import annotations

import json

from spine.L4_runtime.governance.change_proposal_engine import generate_change_proposals
from spine.L4_runtime.governance.state_auditor import audit_state
from spine.L4_runtime.governance.governed_pipeline import run_governed_pipeline

def run(limit: int = 1000):
    report = {
        "proposals": generate_change_proposals(limit=limit),
        "pipeline": run_governed_pipeline(limit=limit),
        "audit": audit_state(),
    }

    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    run()
