"""
Canonical append-only decision-event repository.

The repository:

- accepts validated DecisionEventDraft objects
- rejects duplicate event IDs and idempotency keys
- allocates a monotonic sequence number
- links each new event to the previous event hash
- preserves the canonical Stage 3 content hash
- writes only through TransactionManager
- exposes read methods without mutation methods

The repository does not:

- create tables
- run migrations
- create sessions or engines
- expose update or delete operations
- modify application runtime composition
- expose API routes
- enable broker execution
- enable live trading

Cross-process sequence-allocation qualification and the database migration
remain deferred to the next stage.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Protocol, cast
from uuid import UUID

from sqlalchemy import (
    Select,
    desc,
    select,
    text,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from backend.app.stacks.db_runtime.transaction_manager import (
    TransactionManager,
    TransactionSession,
)
from backend.app.stacks.journal_ledger.decision_event_contract import (
    DecisionEventDraft,
    PersistedDecisionEvent,
)
from backend.app.stacks.journal_ledger.decision_event_model import (
    DecisionEventRecord,
)


class DecisionEventRepositoryError(
    RuntimeError,
):
    """Base repository failure."""


class DuplicateDecisionEventError(
    DecisionEventRepositoryError,
):
    """Raised when an event ID or idempotency key already exists."""


class DecisionEventNotFoundError(
    DecisionEventRepositoryError,
):
    """Raised when a requested event does not exist."""


class DecisionEventIntegrityError(
    DecisionEventRepositoryError,
):
    """Raised when persisted chain data violates the contract."""


class ScalarResultLike(
    Protocol,
):
    def scalar_one_or_none(
        self,
    ) -> object | None:
        """Return one scalar or None."""

    def scalars(
        self,
    ) -> object:
        """Return scalar collection."""


class RepositorySession(
    TransactionSession,
    Protocol,
):
    def add(
        self,
        instance: object,
    ) -> None:
        """Stage an ORM insert."""

    async def execute(
        self,
        statement: object,
    ) -> ScalarResultLike:
        """Execute a SQLAlchemy statement."""


class DecisionEventRepository:
    """
    Append-only decision-event persistence boundary.

    This class intentionally exposes no update(), merge(), replace(),
    delete(), purge(), or truncate() method.
    """

    # PostgreSQL transaction-scoped advisory-lock namespace.
    #
    # All decision-event append operations use this same stable pair,
    # serializing sequence allocation and hash-chain linkage across
    # sessions and processes. PostgreSQL releases the lock automatically
    # when TransactionManager commits or rolls back.
    _APPEND_LOCK_NAMESPACE = 3
    _APPEND_LOCK_RESOURCE = 5

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session
        self._transactions = TransactionManager(
            cast(
                TransactionSession,
                session,
            )
        )

    @property
    def session(
        self,
    ) -> AsyncSession:
        return self._session

    async def append(
        self,
        draft: DecisionEventDraft,
        *,
        recorded_at: datetime | None = None,
    ) -> PersistedDecisionEvent:
        if not isinstance(
            draft,
            DecisionEventDraft,
        ):
            raise TypeError(
                "draft must be a DecisionEventDraft"
            )

        effective_recorded_at = (
            recorded_at
            if recorded_at is not None
            else datetime.now(
                UTC
            )
        )

        if (
            effective_recorded_at.tzinfo is None
            or effective_recorded_at.utcoffset() is None
        ):
            raise DecisionEventRepositoryError(
                "recorded_at must be timezone-aware"
            )

        effective_recorded_at = (
            effective_recorded_at.astimezone(
                UTC
            )
        )

        async def operation(
            transaction_session: TransactionSession,
        ) -> PersistedDecisionEvent:
            session = cast(
                RepositorySession,
                transaction_session,
            )

            await self._acquire_append_lock(
                session
            )

            await self._ensure_unique(
                session,
                event_id=draft.event_id,
                idempotency_key=(
                    draft.idempotency_key
                ),
            )

            previous = await self._latest_record(
                session,
                lock_for_append=True,
            )

            if previous is None:
                sequence_number = 1
                previous_hash = None
            else:
                sequence_number = (
                    previous.sequence_number
                    + 1
                )

                previous_hash = (
                    previous.content_hash
                )

            content_hash = (
                draft.content_hash()
            )

            record = DecisionEventRecord(
                sequence_number=sequence_number,
                event_id=str(
                    draft.event_id
                ),
                idempotency_key=(
                    draft.idempotency_key
                ),
                event_type=(
                    draft.event_type.value
                ),
                outcome=(
                    draft.outcome.value
                ),
                occurred_at=(
                    draft.occurred_at
                ),
                recorded_at=(
                    effective_recorded_at
                ),
                actor=draft.actor,
                source=draft.source,
                correlation_id=str(
                    draft.correlation_id
                ),
                causation_id=(
                    str(
                        draft.causation_id
                    )
                    if draft.causation_id
                    else None
                ),
                symbol=draft.symbol,
                confidence=(
                    draft.confidence
                ),
                reason=draft.reason,
                payload=dict(
                    draft.payload
                ),
                previous_hash=(
                    previous_hash
                ),
                content_hash=(
                    content_hash
                ),
                contract_version=1,
            )

            session.add(
                record
            )

            return PersistedDecisionEvent(
                sequence_number=(
                    sequence_number
                ),
                recorded_at=(
                    effective_recorded_at
                ),
                previous_hash=(
                    previous_hash
                ),
                content_hash=(
                    content_hash
                ),
                draft=draft,
            )

        return await self._transactions.execute(
            operation
        )

    async def get_by_event_id(
        self,
        event_id: UUID,
    ) -> PersistedDecisionEvent | None:
        statement = select(
            DecisionEventRecord
        ).where(
            DecisionEventRecord.event_id
            == str(
                event_id
            )
        )

        result = await self._session.execute(
            statement
        )

        record = result.scalar_one_or_none()

        if record is None:
            return None

        return self._to_contract(
            cast(
                DecisionEventRecord,
                record,
            )
        )

    async def get_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> PersistedDecisionEvent | None:
        normalized = idempotency_key.strip()

        if not normalized:
            raise ValueError(
                "idempotency_key must not be empty"
            )

        statement = select(
            DecisionEventRecord
        ).where(
            DecisionEventRecord.idempotency_key
            == normalized
        )

        result = await self._session.execute(
            statement
        )

        record = result.scalar_one_or_none()

        if record is None:
            return None

        return self._to_contract(
            cast(
                DecisionEventRecord,
                record,
            )
        )

    async def latest(
        self,
    ) -> PersistedDecisionEvent | None:
        record = await self._latest_record(
            cast(
                RepositorySession,
                self._session,
            ),
            lock_for_append=False,
        )

        if record is None:
            return None

        return self._to_contract(
            record
        )

    async def list_recent(
        self,
        *,
        limit: int = 100,
    ) -> tuple[PersistedDecisionEvent, ...]:
        if (
            not isinstance(
                limit,
                int,
            )
            or isinstance(
                limit,
                bool,
            )
            or limit < 1
            or limit > 1000
        ):
            raise ValueError(
                "limit must be an integer between 1 and 1000"
            )

        statement = (
            select(
                DecisionEventRecord
            )
            .order_by(
                desc(
                    DecisionEventRecord.sequence_number
                )
            )
            .limit(
                limit
            )
        )

        result = await self._session.execute(
            statement
        )

        scalar_result = result.scalars()

        all_method = getattr(
            scalar_result,
            "all",
            None,
        )

        if not callable(
            all_method
        ):
            raise DecisionEventRepositoryError(
                "session result does not expose scalars().all()"
            )

        records = all_method()

        return tuple(
            self._to_contract(
                cast(
                    DecisionEventRecord,
                    record,
                )
            )
            for record in records
        )

    async def _acquire_append_lock(
        self,
        session: RepositorySession,
    ) -> None:
        """
        Serialize decision-event append allocation in PostgreSQL.

        Row-level locking alone cannot protect an empty ledger because
        there is no row to lock. It can also permit competing sessions
        to calculate the same successor while working from the same
        latest record.

        A transaction-scoped PostgreSQL advisory lock protects the
        complete allocation operation:

        - uniqueness inspection
        - latest-record selection
        - sequence allocation
        - previous-hash linkage
        - insert and flush

        The lock is released automatically when TransactionManager
        commits or rolls back the active transaction.
        """

        if not isinstance(
            self._session,
            AsyncSession,
        ):
            return

        bind = self._session.get_bind()

        if bind.dialect.name != "postgresql":
            return

        await session.execute(
            text(
                "SELECT pg_advisory_xact_lock("
                ":namespace, :resource"
                ")"
            ),
            {
                "namespace": (
                    self._APPEND_LOCK_NAMESPACE
                ),
                "resource": (
                    self._APPEND_LOCK_RESOURCE
                ),
            },
        )

    async def _ensure_unique(
        self,
        session: RepositorySession,
        *,
        event_id: UUID,
        idempotency_key: str,
    ) -> None:
        statement = select(
            DecisionEventRecord
        ).where(
            (
                DecisionEventRecord.event_id
                == str(
                    event_id
                )
            )
            | (
                DecisionEventRecord.idempotency_key
                == idempotency_key
            )
        )

        result = await session.execute(
            statement
        )

        existing = result.scalar_one_or_none()

        if existing is not None:
            raise DuplicateDecisionEventError(
                "decision event already exists for "
                "event_id or idempotency_key"
            )

    async def _latest_record(
        self,
        session: RepositorySession,
        *,
        lock_for_append: bool,
    ) -> DecisionEventRecord | None:
        statement: Select[
            tuple[
                DecisionEventRecord
            ]
        ] = (
            select(
                DecisionEventRecord
            )
            .order_by(
                desc(
                    DecisionEventRecord.sequence_number
                )
            )
            .limit(
                1
            )
        )

        if lock_for_append:
            statement = statement.with_for_update()

        result = await session.execute(
            statement
        )

        record = result.scalar_one_or_none()

        if record is None:
            return None

        return cast(
            DecisionEventRecord,
            record,
        )

    @staticmethod
    def _to_contract(
        record: DecisionEventRecord,
    ) -> PersistedDecisionEvent:
        from backend.app.stacks.journal_ledger.decision_event_contract import (
            DecisionEventType,
            DecisionOutcome,
        )

        try:
            draft = DecisionEventDraft(
                event_id=UUID(
                    record.event_id
                ),
                idempotency_key=(
                    record.idempotency_key
                ),
                event_type=(
                    DecisionEventType(
                        record.event_type
                    )
                ),
                outcome=(
                    DecisionOutcome(
                        record.outcome
                    )
                ),
                occurred_at=(
                    record.occurred_at
                ),
                actor=record.actor,
                source=record.source,
                correlation_id=UUID(
                    record.correlation_id
                ),
                causation_id=(
                    UUID(
                        record.causation_id
                    )
                    if record.causation_id
                    else None
                ),
                symbol=record.symbol,
                confidence=(
                    record.confidence
                ),
                reason=record.reason,
                payload=record.payload,
            )

            return PersistedDecisionEvent(
                sequence_number=(
                    record.sequence_number
                ),
                recorded_at=(
                    record.recorded_at
                ),
                previous_hash=(
                    record.previous_hash
                ),
                content_hash=(
                    record.content_hash
                ),
                draft=draft,
            )

        except Exception as exc:
            raise DecisionEventIntegrityError(
                "persisted decision event violates "
                "the canonical contract"
            ) from exc
