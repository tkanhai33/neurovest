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
