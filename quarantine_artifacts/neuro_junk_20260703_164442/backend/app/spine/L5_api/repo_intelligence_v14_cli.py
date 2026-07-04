from __future__ import annotations

import json

from spine.L4_runtime.memory.state_replay_engine import replay_state
from spine.L4_runtime.governance.action_enforcer_v2 import enforce_action_v2
from spine.L4_runtime.governance.change_proposal_engine import generate_change_proposals

def run(limit: int = 1000):
    proposals = generate_change_proposals(limit=limit)["proposals"]

    results = []

    for p in proposals:
        results.append(enforce_action_v2(p))

    report = {
        "execution_results": results[:10],
        "replay": replay_state()
    }

    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    run()
