"""DOMAIN_LOGIC_V1 in-memory journal ledger."""

from stacks.journal_ledger.record import make_ledger_record


def record_event(
    event_type: str,
    payload: dict,
    ledger: list[dict] | None = None,
) -> list[dict]:
    ledger = ledger if ledger is not None else []
    ledger.append(make_ledger_record(event_type, payload))
    return ledger
