from __future__ import annotations
from spine.L4_runtime.governance.change_proposal_engine import generate_change_proposals
from spine.L4_runtime.sandbox.simulation_engine import simulate_change
def run_sandbox(limit: int = 1000) -> dict:
    proposals = generate_change_proposals(limit=limit)["proposals"]
    results = []
    safe = []
    rejected = []
    for p in proposals:
        sim = simulate_change(p)
        results.append(sim)
        if sim["safe"]:
            safe.append(p)
        else:
            rejected.append(p)
    return {
    }
