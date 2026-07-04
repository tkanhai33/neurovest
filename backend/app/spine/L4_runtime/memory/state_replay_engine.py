from __future__ import annotations
import json
from pathlib import Path
EVENT_LOG = Path("backend/app/spine/L4_runtime/memory/event_log.json")
def replay_state() -> dict:
    if not EVENT_LOG.exists():
        return {
        }
    events = json.loads(EVENT_LOG.read_text())
    state = {}
    for e in events:
        stack = e.get("stack")
        value = e.get("value")
        if stack:
            state[stack] = value
    return {
    }
