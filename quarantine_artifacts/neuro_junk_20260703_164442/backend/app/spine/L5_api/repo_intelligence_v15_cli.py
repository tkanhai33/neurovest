from __future__ import annotations

import json

from spine.L4_runtime.signals.signal_to_proposal import translate_signals
from spine.L4_runtime.governance.approval_state_machine import run_approval_flow
from spine.L4_runtime.memory.state_event_store import append_event
from spine.L4_runtime.memory.state_replay_engine import replay_state

def run(limit: int = 1000):
    bundle = translate_signals(limit=limit)

    results = []

    for p in bundle["proposals"]:
        decision = run_approval_flow(p)

        if decision["state"] == "APPROVED":
            append_event({
                "stack": p["stack"],
                "value": f"updated:{p['target']}",
                "type": "SIGNAL_EXECUTION"
            })

        results.append(decision)

    report = {
        "signal_count": bundle["signal_count"],
        "executed": sum(1 for r in results if r["state"] == "APPROVED"),
        "replay": replay_state()
    }

    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    run()
