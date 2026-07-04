"""DOMAIN_LOGIC_V1 journal record creation."""

from datetime import datetime, UTC


def make_ledger_record(event_type: str, payload: dict) -> dict:
    return {
        "event_type": event_type,
        "payload": payload,
        "timestamp": datetime.now(UTC).isoformat(),
    }
