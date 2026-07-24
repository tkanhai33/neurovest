"""
Canonical append-only decision-event ORM model.

This model belongs exclusively to:

    backend.app.stacks.db_runtime.database.Base

The model does not:

- create its table
- run a migration
- open a database connection
- register an API route
- modify runtime composition
- authorize broker execution
- enable live trading

Update and delete operations are rejected through SQLAlchemy mapper
events. The only supported persistence action is insertion.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
    event,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from backend.app.stacks.db_runtime.database import (
    Base,
)


class AppendOnlyViolation(
    RuntimeError,
):
    """Raised when an existing decision event is updated or deleted."""


class DecisionEventRecord(
    Base,
):
    """
    Canonical persisted decision-event record.

    Records are insert-only. Existing rows must never be edited,
    overwritten, merged into a different value, or deleted.
    """

    __tablename__ = "decision_events"

    __table_args__ = (
        UniqueConstraint(
            "event_id",
            name="uq_decision_events_event_id",
        ),
        UniqueConstraint(
            "idempotency_key",
            name="uq_decision_events_idempotency_key",
        ),
        UniqueConstraint(
            "content_hash",
            name="uq_decision_events_content_hash",
        ),
        CheckConstraint(
            "sequence_number >= 1",
            name="ck_decision_events_positive_sequence",
        ),
        CheckConstraint(
            "confidence IS NULL OR "
            "(confidence >= 0.0 AND confidence <= 1.0)",
            name="ck_decision_events_confidence_range",
        ),
        CheckConstraint(
            "("
            "sequence_number = 1 AND previous_hash IS NULL"
            ") OR ("
            "sequence_number > 1 AND previous_hash IS NOT NULL"
            ")",
            name="ck_decision_events_previous_hash",
        ),
    )

    sequence_number: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=False,
    )

    event_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
    )

    idempotency_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    event_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    outcome: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(
            timezone=True
        ),
        nullable=False,
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(
            timezone=True
        ),
        nullable=False,
    )

    actor: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    source: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    correlation_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
    )

    causation_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        index=True,
    )

    symbol: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
        index=True,
    )

    confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    payload: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
    )

    previous_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    content_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    contract_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    def __repr__(
        self,
    ) -> str:
        return (
            "DecisionEventRecord("
            f"sequence_number={self.sequence_number!r}, "
            f"event_id={self.event_id!r}, "
            f"event_type={self.event_type!r}, "
            f"outcome={self.outcome!r}"
            ")"
        )


@event.listens_for(
    DecisionEventRecord,
    "before_update",
    propagate=True,
)
def reject_decision_event_update(
    mapper: object,
    connection: object,
    target: DecisionEventRecord,
) -> None:
    del mapper
    del connection
    del target

    raise AppendOnlyViolation(
        "decision events are append-only and cannot be updated"
    )


@event.listens_for(
    DecisionEventRecord,
    "before_delete",
    propagate=True,
)
def reject_decision_event_delete(
    mapper: object,
    connection: object,
    target: DecisionEventRecord,
) -> None:
    del mapper
    del connection
    del target

    raise AppendOnlyViolation(
        "decision events are append-only and cannot be deleted"
    )
