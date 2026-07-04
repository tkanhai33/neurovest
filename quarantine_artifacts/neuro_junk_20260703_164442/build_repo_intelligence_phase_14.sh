#!/bin/bash
set -e

echo "🧠 Phase 14 — State Memory + Replay Engine"

mkdir -p backend/app/spine/L4_runtime/memory
mkdir -p backend/app/spine/L5_api
mkdir -p backend/app/spine/L7_tests

# =========================================================
# FILE 1 — STATE EVENT STORE
# =========================================================
cat > backend/app/spine/L4_runtime/memory/state_event_store.py <<'PY'
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime

EVENT_LOG = Path("backend/app/spine/L4_runtime/memory/event_log.json")

def append_event(event: dict) -> None:
    EVENT_LOG.parent.mkdir(parents=True, exist_ok=True)

    log = []
    if EVENT_LOG.exists():
        try:
            log = json.loads(EVENT_LOG.read_text())
        except Exception:
            log = []

    event["timestamp"] = datetime.utcnow().isoformat()
    log.append(event)

    EVENT_LOG.write_text(json.dumps(log, indent=2))
PY


# =========================================================
# FILE 2 — STATE REPLAY ENGINE
# =========================================================
cat > backend/app/spine/L4_runtime/memory/state_replay_engine.py <<'PY'
from __future__ import annotations

import json
from pathlib import Path

EVENT_LOG = Path("backend/app/spine/L4_runtime/memory/event_log.json")

def replay_state() -> dict:
    if not EVENT_LOG.exists():
        return {
            "replay": [],
            "final_state": {}
        }

    events = json.loads(EVENT_LOG.read_text())

    state = {}

    for e in events:
        stack = e.get("stack")
        value = e.get("value")

        if stack:
            state[stack] = value

    return {
        "event_count": len(events),
        "final_state": state,
        "replay": events[-10:]
    }
PY


# =========================================================
# FILE 3 — ENHANCED ACTION ENFORCER (PERSISTENT)
# =========================================================
cat > backend/app/spine/L4_runtime/governance/action_enforcer_v2.py <<'PY'
from __future__ import annotations

from spine.L4_runtime.governance.approval_state_machine import run_approval_flow
from spine.L4_runtime.memory.state_event_store import append_event

SYSTEM_STATE = {
    "risk": "idle",
    "strategy": "idle",
    "execution": "idle",
    "portfolio": "idle"
}

def enforce_action_v2(proposal: dict) -> dict:
    result = run_approval_flow(proposal)

    stack = proposal.get("stack")
    target = proposal.get("target")

    if result["state"] == "APPROVED":
        value = f"updated:{target}"
        SYSTEM_STATE[stack] = value

        append_event({
            "stack": stack,
            "value": value,
            "type": "STATE_MUTATION"
        })

        action_taken = True
    else:
        action_taken = False

    return {
        "proposal": proposal,
        "state": result["state"],
        "action_taken": action_taken,
        "system_state": dict(SYSTEM_STATE)
    }
PY


# =========================================================
# FILE 4 — REPLAY CLI
# =========================================================
cat > backend/app/spine/L5_api/repo_intelligence_v14_cli.py <<'PY'
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
PY


# =========================================================
# FILE 5 — TESTS
# =========================================================
cat > backend/app/spine/L7_tests/test_phase14_memory.py <<'PY'
from spine.L4_runtime.memory.state_event_store import append_event
from spine.L4_runtime.memory.state_replay_engine import replay_state

def test_event_store():
    append_event({"stack": "risk", "value": "test"})
    r = replay_state()
    assert "final_state" in r
PY


# =========================================================
# EXECUTION
# =========================================================

echo "🧠 Running Phase 14 CLI..."
PYTHONPATH=backend/app python3 backend/app/spine/L5_api/repo_intelligence_v14_cli.py

echo "🧪 Running Phase 14 tests..."
PYTHONPATH=backend/app pytest -q backend/app/spine/L7_tests/test_phase14_memory.py

echo "✅ Phase 14 Complete"
