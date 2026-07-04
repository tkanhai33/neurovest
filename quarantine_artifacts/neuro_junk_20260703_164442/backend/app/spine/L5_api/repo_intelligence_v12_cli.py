from __future__ import annotations

import json

from spine.L4_runtime.governance.change_proposal_engine import generate_change_proposals
from spine.L4_runtime.governance.approval_state_machine import run_approval_flow
from spine.L4_runtime.governance.execution_log import log_decision

def run(limit: int = 1000):
    proposals = generate_change_proposals(limit=limit)["proposals"]

    results = []

    for p in proposals:
        decision = run_approval_flow(p)
        log_decision(decision)
        results.append(decision)

    summary = {
        "total": len(results),
        "approved": sum(1 for r in results if r["state"] == "APPROVED"),
        "rejected": sum(1 for r in results if r["state"] == "REJECTED"),
        "results": results[:10]  # preview only
    }

    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    run()
