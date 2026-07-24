#!/usr/bin/env python3

from __future__ import annotations

import asyncio
import json

from backend.app.core.cognitive_graph_state import graph_state
from backend.app.stacks.events.broker import global_event_bus


async def main() -> None:
    event = await global_event_bus.emit(
        "PHASE_133B_VALIDATION",
        {
            "node": "graph_live",
            "from": "events_broker",
            "to": "graph_live",
            "status": "completed",
            "message": "Activation contract validation",
        },
    )

    trace_id = event["trace_id"]
    snapshot = graph_state.snapshot()

    matching_steps = [
        step
        for step in snapshot["recent_flows"]
        if step.get("trace_id") == trace_id
    ]

    assert matching_steps, "No trace steps recorded."
    assert any(
        step.get("record_type") == "node_activation"
        for step in matching_steps
    ), "Node activation missing."
    assert any(
        step.get("record_type") == "edge_activation"
        for step in matching_steps
    ), "Edge activation missing."

    sequences = [
        int(step["sequence"])
        for step in matching_steps
    ]

    assert sequences == sorted(sequences), (
        "Trace sequence is not ordered."
    )

    result = {
        "phase": "133B_ACTIVE_NODE_FLOW_GRAPH",
        "contract": "activation_event_v1",
        "trace_id": trace_id,
        "steps": matching_steps,
        "sequence_ordered": True,
        "node_activation_present": True,
        "edge_activation_present": True,
        "synthetic_runtime_flow_claimed": False,
        "certified": True,
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
