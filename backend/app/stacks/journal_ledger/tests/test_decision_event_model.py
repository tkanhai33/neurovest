from __future__ import annotations

from sqlalchemy import inspect

from backend.app.stacks.db_runtime.database import (
    Base,
)
from backend.app.stacks.journal_ledger.decision_event_model import (
    AppendOnlyViolation,
    DecisionEventRecord,
    reject_decision_event_delete,
    reject_decision_event_update,
)


def test_model_uses_canonical_runtime_base() -> None:
    assert issubclass(
        DecisionEventRecord,
        Base,
    )

    assert (
        DecisionEventRecord.metadata
        is Base.metadata
    )


def test_table_name_is_canonical() -> None:
    assert (
        DecisionEventRecord.__tablename__
        == "decision_events"
    )


def test_required_constraints_and_columns_exist() -> None:
    mapper = inspect(
        DecisionEventRecord
    )

    columns = {
        column.key
        for column in mapper.columns
    }

    required = {
        "sequence_number",
        "event_id",
        "idempotency_key",
        "event_type",
        "outcome",
        "occurred_at",
        "recorded_at",
        "actor",
        "source",
        "correlation_id",
        "causation_id",
        "symbol",
        "confidence",
        "reason",
        "payload",
        "previous_hash",
        "content_hash",
        "contract_version",
    }

    assert required == columns

    table = DecisionEventRecord.__table__

    unique_names = {
        constraint.name
        for constraint in table.constraints
        if constraint.name
        and constraint.name.startswith(
            "uq_"
        )
    }

    assert {
        "uq_decision_events_event_id",
        "uq_decision_events_idempotency_key",
        "uq_decision_events_content_hash",
    }.issubset(
        unique_names
    )


def test_sequence_number_is_primary_key() -> None:
    table = DecisionEventRecord.__table__

    primary_keys = [
        column.name
        for column in table.primary_key.columns
    ]

    assert primary_keys == [
        "sequence_number"
    ]


def test_update_listener_rejects_mutation() -> None:
    record = DecisionEventRecord()

    try:
        reject_decision_event_update(
            object(),
            object(),
            record,
        )

    except AppendOnlyViolation as exc:
        assert "cannot be updated" in str(
            exc
        )

    else:
        raise AssertionError(
            "update listener did not reject mutation"
        )


def test_delete_listener_rejects_mutation() -> None:
    record = DecisionEventRecord()

    try:
        reject_decision_event_delete(
            object(),
            object(),
            record,
        )

    except AppendOnlyViolation as exc:
        assert "cannot be deleted" in str(
            exc
        )

    else:
        raise AssertionError(
            "delete listener did not reject mutation"
        )
