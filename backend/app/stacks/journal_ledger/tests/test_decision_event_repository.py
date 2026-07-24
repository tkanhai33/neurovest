from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import pytest

from backend.app.stacks.journal_ledger.decision_event_contract import (
    DecisionEventDraft,
    DecisionEventType,
    DecisionOutcome,
)
from backend.app.stacks.journal_ledger.decision_event_model import (
    DecisionEventRecord,
)
from backend.app.stacks.journal_ledger.decision_event_repository import (
    DecisionEventRepository,
    DuplicateDecisionEventError,
)


EVENT_ID = UUID(
    "00000000-0000-0000-0000-000000000101"
)

SECOND_EVENT_ID = UUID(
    "00000000-0000-0000-0000-000000000102"
)

CORRELATION_ID = UUID(
    "00000000-0000-0000-0000-000000000103"
)

OCCURRED_AT = datetime(
    2026,
    7,
    10,
    20,
    0,
    tzinfo=UTC,
)


def make_draft(
    *,
    event_id: UUID = EVENT_ID,
    idempotency_key: str = "risk:AAPL:101",
) -> DecisionEventDraft:
    return DecisionEventDraft(
        event_id=event_id,
        idempotency_key=idempotency_key,
        event_type=(
            DecisionEventType.RISK_DECISION
        ),
        outcome=(
            DecisionOutcome.BLOCKED
        ),
        occurred_at=OCCURRED_AT,
        actor="risk-engine",
        source="risk.stack",
        correlation_id=CORRELATION_ID,
        symbol="AAPL",
        confidence=0.88,
        reason="Exposure threshold exceeded",
        payload={
            "threshold": 0.10,
            "observed": 0.16,
        },
    )


class FakeScalarCollection:
    def __init__(
        self,
        records: list[object],
    ) -> None:
        self._records = records

    def all(
        self,
    ) -> list[object]:
        return list(
            self._records
        )


class FakeResult:
    def __init__(
        self,
        value: object | None = None,
        records: list[object] | None = None,
    ) -> None:
        self._value = value
        self._records = (
            records
            if records is not None
            else []
        )

    def scalar_one_or_none(
        self,
    ) -> object | None:
        return self._value

    def scalars(
        self,
    ) -> FakeScalarCollection:
        return FakeScalarCollection(
            self._records
        )


class FakeSession:
    def __init__(
        self,
        results: list[FakeResult],
        *,
        fail_flush: bool = False,
        fail_commit: bool = False,
    ) -> None:
        self.results = list(
            results
        )

        self.fail_flush = fail_flush
        self.fail_commit = fail_commit

        self.added: list[
            object
        ] = []

        self.events: list[
            str
        ] = []

        self.flush_calls = 0
        self.commit_calls = 0
        self.rollback_calls = 0

    async def execute(
        self,
        statement: object,
    ) -> FakeResult:
        del statement

        self.events.append(
            "execute"
        )

        if not self.results:
            raise AssertionError(
                "unexpected execute call"
            )

        return self.results.pop(
            0
        )

    def add(
        self,
        instance: object,
    ) -> None:
        self.events.append(
            "add"
        )

        self.added.append(
            instance
        )

    async def flush(
        self,
    ) -> None:
        self.events.append(
            "flush"
        )

        self.flush_calls += 1

        if self.fail_flush:
            raise RuntimeError(
                "flush failed"
            )

    async def commit(
        self,
    ) -> None:
        self.events.append(
            "commit"
        )

        self.commit_calls += 1

        if self.fail_commit:
            raise RuntimeError(
                "commit failed"
            )

    async def rollback(
        self,
    ) -> None:
        self.events.append(
            "rollback"
        )

        self.rollback_calls += 1


@pytest.mark.asyncio
async def test_first_append_allocates_sequence_one() -> None:
    session = FakeSession(
        [
            FakeResult(
                None
            ),
            FakeResult(
                None
            ),
        ]
    )

    repository = DecisionEventRepository(
        session  # type: ignore[arg-type]
    )

    draft = make_draft()

    result = await repository.append(
        draft,
        recorded_at=(
            OCCURRED_AT
            + timedelta(
                seconds=1
            )
        ),
    )

    assert result.sequence_number == 1
    assert result.previous_hash is None
    assert result.content_hash == (
        draft.content_hash()
    )

    assert len(
        session.added
    ) == 1

    record = session.added[
        0
    ]

    assert isinstance(
        record,
        DecisionEventRecord,
    )

    assert record.sequence_number == 1
    assert record.event_id == str(
        EVENT_ID
    )
    assert record.idempotency_key == (
        "risk:AAPL:101"
    )

    assert session.events == [
        "execute",
        "execute",
        "add",
        "flush",
        "commit",
    ]


@pytest.mark.asyncio
async def test_second_append_links_previous_hash() -> None:
    previous = DecisionEventRecord(
        sequence_number=7,
        event_id=str(
            UUID(
                "00000000-0000-0000-0000-000000000099"
            )
        ),
        idempotency_key="previous",
        event_type="risk_decision",
        outcome="blocked",
        occurred_at=OCCURRED_AT,
        recorded_at=(
            OCCURRED_AT
            + timedelta(
                seconds=1
            )
        ),
        actor="risk-engine",
        source="risk.stack",
        correlation_id=str(
            CORRELATION_ID
        ),
        causation_id=None,
        symbol="AAPL",
        confidence=0.80,
        reason="previous",
        payload={},
        previous_hash=(
            "a"
            * 64
        ),
        content_hash=(
            "b"
            * 64
        ),
        contract_version=1,
    )

    session = FakeSession(
        [
            FakeResult(
                None
            ),
            FakeResult(
                previous
            ),
        ]
    )

    repository = DecisionEventRepository(
        session  # type: ignore[arg-type]
    )

    draft = make_draft(
        event_id=SECOND_EVENT_ID,
        idempotency_key="risk:AAPL:102",
    )

    result = await repository.append(
        draft,
        recorded_at=(
            OCCURRED_AT
            + timedelta(
                seconds=2
            )
        ),
    )

    assert result.sequence_number == 8
    assert result.previous_hash == (
        "b"
        * 64
    )

    record = session.added[
        0
    ]

    assert isinstance(
        record,
        DecisionEventRecord,
    )

    assert record.sequence_number == 8
    assert record.previous_hash == (
        "b"
        * 64
    )


@pytest.mark.asyncio
async def test_duplicate_is_rejected_before_insert() -> None:
    existing = DecisionEventRecord(
        sequence_number=1,
        event_id=str(
            EVENT_ID
        ),
        idempotency_key="risk:AAPL:101",
        event_type="risk_decision",
        outcome="blocked",
        occurred_at=OCCURRED_AT,
        recorded_at=(
            OCCURRED_AT
            + timedelta(
                seconds=1
            )
        ),
        actor="risk-engine",
        source="risk.stack",
        correlation_id=str(
            CORRELATION_ID
        ),
        causation_id=None,
        symbol="AAPL",
        confidence=0.88,
        reason="existing",
        payload={},
        previous_hash=None,
        content_hash=(
            "c"
            * 64
        ),
        contract_version=1,
    )

    session = FakeSession(
        [
            FakeResult(
                existing
            ),
        ]
    )

    repository = DecisionEventRepository(
        session  # type: ignore[arg-type]
    )

    with pytest.raises(
        DuplicateDecisionEventError,
    ):
        await repository.append(
            make_draft(),
            recorded_at=(
                OCCURRED_AT
                + timedelta(
                    seconds=1
                )
            ),
        )

    assert session.added == []
    assert session.flush_calls == 0
    assert session.commit_calls == 0
    assert session.rollback_calls == 1


@pytest.mark.asyncio
async def test_commit_failure_rolls_back() -> None:
    session = FakeSession(
        [
            FakeResult(
                None
            ),
            FakeResult(
                None
            ),
        ],
        fail_commit=True,
    )

    repository = DecisionEventRepository(
        session  # type: ignore[arg-type]
    )

    with pytest.raises(
        RuntimeError,
        match="commit failed",
    ):
        await repository.append(
            make_draft(),
            recorded_at=(
                OCCURRED_AT
                + timedelta(
                    seconds=1
                )
            ),
        )

    assert session.flush_calls == 1
    assert session.commit_calls == 1
    assert session.rollback_calls == 1


def test_repository_exposes_no_mutation_methods() -> None:
    forbidden = {
        "update",
        "delete",
        "remove",
        "purge",
        "truncate",
        "replace",
        "merge",
    }

    exposed = {
        name
        for name in dir(
            DecisionEventRepository
        )
        if not name.startswith(
            "_"
        )
    }

    assert forbidden.isdisjoint(
        exposed
    )


@pytest.mark.asyncio
async def test_append_rejects_naive_recorded_at() -> None:
    session = FakeSession(
        []
    )

    repository = DecisionEventRepository(
        session  # type: ignore[arg-type]
    )

    with pytest.raises(
        Exception,
        match="timezone-aware",
    ):
        await repository.append(
            make_draft(),
            recorded_at=datetime(
                2026,
                7,
                10,
                20,
                1,
            ),
        )

    assert session.events == []
