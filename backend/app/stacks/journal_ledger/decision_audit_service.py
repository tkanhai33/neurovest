"""
Canonical append-only decision audit service.

Ownership
---------
Stack:
    journal_ledger

Persistence:
    DecisionEventRepository

Transaction ownership:
    DecisionEventRepository and TransactionManager

This service intentionally exposes:

- append
- read by event ID
- read by idempotency key
- latest event
- recent events

This service intentionally exposes no update, delete, replace,
merge, purge, truncate, or mutable-ledger operation.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.stacks.journal_ledger.decision_event_contract import (
    DecisionEventDraft,
    PersistedDecisionEvent,
)
from backend.app.stacks.journal_ledger.decision_event_repository import (
    DecisionEventRepository,
)


class DecisionAuditService:
    """
    Canonical application-facing decision audit boundary.

    The service does not own commits, rollbacks, sequence allocation,
    hash-chain construction, or duplicate enforcement. Those guarantees
    remain inside DecisionEventRepository and TransactionManager.
    """

    def __init__(
        self,
        repository: DecisionEventRepository,
    ) -> None:
        self._repository = repository

    async def append(
        self,
        draft: DecisionEventDraft,
        *,
        recorded_at: datetime | None = None,
    ) -> PersistedDecisionEvent:
        """
        Append one immutable decision event.

        This is the only write operation exposed by this service.
        """

        return await self._repository.append(
            draft,
            recorded_at=recorded_at,
        )

    async def get_by_event_id(
        self,
        event_id: UUID,
    ) -> PersistedDecisionEvent | None:
        """Return one event by canonical event identifier."""

        return await self._repository.get_by_event_id(
            event_id
        )

    async def get_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> PersistedDecisionEvent | None:
        """Return one event by idempotency key."""

        return await self._repository.get_by_idempotency_key(
            idempotency_key
        )

    async def latest(
        self,
    ) -> PersistedDecisionEvent | None:
        """Return the latest persisted decision event."""

        return await self._repository.latest()

    async def list_recent(
        self,
        *,
        limit: int = 100,
    ) -> tuple[PersistedDecisionEvent, ...]:
        """
        Return recent events in repository-defined canonical order.
        """

        if isinstance(
            limit,
            bool,
        ) or not isinstance(
            limit,
            int,
        ):
            raise TypeError(
                "limit must be an integer"
            )

        if limit < 1:
            raise ValueError(
                "limit must be at least 1"
            )

        if limit > 1000:
            raise ValueError(
                "limit must not exceed 1000"
            )

        events = await self._repository.list_recent(
            limit=limit
        )

        return tuple(
            events
        )


def build_decision_audit_service(
    session: AsyncSession,
) -> DecisionAuditService:
    """
    Build the canonical service for one database session.

    No process-global mutable repository or session is created.
    """

    return DecisionAuditService(
        DecisionEventRepository(
            session
        )
    )
