from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from backend.app.stacks.journal_ledger.decision_audit_service import (
    DecisionAuditService,
)
from backend.app.stacks.journal_ledger.decision_event_contract import (
    DecisionEventDraft,
)


class FakeRepository:
    def __init__(self) -> None:
        self.append = AsyncMock()
        self.get_by_event_id = AsyncMock()
        self.get_by_idempotency_key = AsyncMock()
        self.latest = AsyncMock()
        self.list_recent = AsyncMock()


def test_service_exposes_append_and_read_methods_only() -> None:
    public_methods = {
        name
        for name in dir(
            DecisionAuditService
        )
        if (
            not name.startswith("_")
            and callable(
                getattr(
                    DecisionAuditService,
                    name,
                )
            )
        )
    }

    assert {
        "append",
        "get_by_event_id",
        "get_by_idempotency_key",
        "latest",
        "list_recent",
    }.issubset(
        public_methods
    )

    forbidden = {
        "update",
        "delete",
        "remove",
        "replace",
        "merge",
        "purge",
        "truncate",
    }

    assert forbidden.isdisjoint(
        public_methods
    )


@pytest.mark.asyncio
async def test_append_delegates_to_repository() -> None:
    repository = FakeRepository()
    service = DecisionAuditService(
        repository  # type: ignore[arg-type]
    )

    draft = object()
    recorded_at = datetime.now(
        UTC
    )
    persisted = object()

    repository.append.return_value = (
        persisted
    )

    result = await service.append(
        draft,  # type: ignore[arg-type]
        recorded_at=recorded_at,
    )

    assert result is persisted

    repository.append.assert_awaited_once_with(
        draft,
        recorded_at=recorded_at,
    )


@pytest.mark.asyncio
async def test_read_methods_delegate_to_repository() -> None:
    repository = FakeRepository()
    service = DecisionAuditService(
        repository  # type: ignore[arg-type]
    )

    event_id = uuid4()
    idempotency_key = "stage6-key"

    event_by_id = object()
    event_by_key = object()
    latest_event = object()
    recent_events = [
        object(),
        object(),
    ]

    repository.get_by_event_id.return_value = (
        event_by_id
    )

    repository.get_by_idempotency_key.return_value = (
        event_by_key
    )

    repository.latest.return_value = (
        latest_event
    )

    repository.list_recent.return_value = (
        recent_events
    )

    assert (
        await service.get_by_event_id(
            event_id
        )
        is event_by_id
    )

    assert (
        await service.get_by_idempotency_key(
            idempotency_key
        )
        is event_by_key
    )

    assert (
        await service.latest()
        is latest_event
    )

    assert (
        await service.list_recent(
            limit=2
        )
        == tuple(
            recent_events
        )
    )

    repository.get_by_event_id.assert_awaited_once_with(
        event_id
    )

    repository.get_by_idempotency_key.assert_awaited_once_with(
        idempotency_key
    )

    repository.latest.assert_awaited_once_with()

    repository.list_recent.assert_awaited_once_with(
        limit=2
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "limit,exception",
    [
        (True, TypeError),
        (1.5, TypeError),
        (0, ValueError),
        (-1, ValueError),
        (1001, ValueError),
    ],
)
async def test_list_recent_rejects_invalid_limits(
    limit: object,
    exception: type[Exception],
) -> None:
    repository = FakeRepository()
    service = DecisionAuditService(
        repository  # type: ignore[arg-type]
    )

    with pytest.raises(
        exception
    ):
        await service.list_recent(
            limit=limit,  # type: ignore[arg-type]
        )

    repository.list_recent.assert_not_awaited()
