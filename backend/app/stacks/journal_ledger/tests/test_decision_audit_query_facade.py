from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from types import MappingProxyType
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest

from backend.app.stacks.journal_ledger.decision_audit_query_facade import (
    DecisionAuditQueryFacade,
    SerializedDecisionAuditDTO,
)
from backend.app.stacks.journal_ledger.decision_audit_service import (
    DecisionAuditService,
)


@dataclass(
    frozen=True,
    slots=True,
)
class FixtureDecisionAuditRecord:
    event_id: UUID
    idempotency_key: str
    sequence_number: int
    previous_hash: str | None
    content_hash: str
    recorded_at: datetime
    payload: dict[str, object]


def build_record(
    *,
    event_id: UUID | None = None,
    idempotency_key: str = "fixture-key",
    sequence_number: int = 1,
) -> FixtureDecisionAuditRecord:
    return FixtureDecisionAuditRecord(
        event_id=(
            event_id
            or uuid4()
        ),
        idempotency_key=idempotency_key,
        sequence_number=sequence_number,
        previous_hash=None,
        content_hash="fixture-hash",
        recorded_at=datetime(
            2026,
            7,
            11,
            6,
            0,
            tzinfo=UTC,
        ),
        payload={
            "symbol": "AAPL",
            "decision": "HOLD",
            "confidence": 0.75,
        },
    )


def build_service() -> AsyncMock:
    return AsyncMock(
        spec=DecisionAuditService
    )


@pytest.mark.asyncio
async def test_get_by_event_id_delegates_only_to_service() -> None:
    event_id = uuid4()
    record = build_record(
        event_id=event_id
    )

    service = build_service()
    service.get_by_event_id.return_value = record

    facade = DecisionAuditQueryFacade(
        service
    )

    result = await facade.get_by_event_id(
        event_id
    )

    service.get_by_event_id.assert_awaited_once_with(
        event_id
    )

    assert isinstance(
        result,
        SerializedDecisionAuditDTO,
    )

    payload = result.to_dict()

    assert payload[
        "event_id"
    ] == str(
        event_id
    )

    assert payload[
        "payload"
    ]["decision"] == "HOLD"


@pytest.mark.asyncio
async def test_get_by_idempotency_key_normalizes_key() -> None:
    record = build_record(
        idempotency_key="fixture-key"
    )

    service = build_service()

    service.get_by_idempotency_key.return_value = (
        record
    )

    facade = DecisionAuditQueryFacade(
        service
    )

    result = await facade.get_by_idempotency_key(
        "  fixture-key  "
    )

    service.get_by_idempotency_key.assert_awaited_once_with(
        "fixture-key"
    )

    assert result is not None

    assert result.to_dict()[
        "idempotency_key"
    ] == "fixture-key"


@pytest.mark.asyncio
async def test_latest_returns_none_without_exposing_service_record() -> None:
    service = build_service()
    service.latest.return_value = None

    facade = DecisionAuditQueryFacade(
        service
    )

    result = await facade.latest()

    service.latest.assert_awaited_once_with()

    assert result is None


@pytest.mark.asyncio
async def test_list_recent_returns_immutable_tuple_of_serialized_dtos() -> None:
    records = [
        build_record(
            sequence_number=1,
            idempotency_key="key-1",
        ),
        build_record(
            sequence_number=2,
            idempotency_key="key-2",
        ),
    ]

    service = build_service()
    service.list_recent.return_value = records

    facade = DecisionAuditQueryFacade(
        service
    )

    result = await facade.list_recent(
        25
    )

    service.list_recent.assert_awaited_once_with(
        25
    )

    assert isinstance(
        result,
        tuple,
    )

    assert len(
        result
    ) == 2

    assert all(
        isinstance(
            item,
            SerializedDecisionAuditDTO,
        )
        for item in result
    )

    assert result[0].to_dict()[
        "idempotency_key"
    ] == "key-1"


@pytest.mark.asyncio
async def test_serialized_dto_returns_fresh_dictionary_copy() -> None:
    service = build_service()

    service.latest.return_value = (
        build_record()
    )

    facade = DecisionAuditQueryFacade(
        service
    )

    result = await facade.latest()

    assert result is not None

    first = result.to_dict()
    second = result.to_dict()

    assert first == second
    assert first is not second

    first["payload"][
        "decision"
    ] = "BUY"

    assert second[
        "payload"
    ]["decision"] == "HOLD"


@pytest.mark.asyncio
async def test_mapping_proxy_record_is_serialized_without_exposure() -> None:
    service = build_service()

    service.latest.return_value = MappingProxyType(
        {
            "event_id": str(
                uuid4()
            ),
            "decision": "HOLD",
        }
    )

    facade = DecisionAuditQueryFacade(
        service
    )

    result = await facade.latest()

    assert result is not None

    assert result.to_dict()[
        "decision"
    ] == "HOLD"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "invalid_limit",
    [
        0,
        -1,
        1001,
        True,
        1.5,
        "10",
    ],
)
async def test_list_recent_fails_closed_for_invalid_limits(
    invalid_limit: object,
) -> None:
    service = build_service()

    facade = DecisionAuditQueryFacade(
        service
    )

    with pytest.raises(
        (
            TypeError,
            ValueError,
        )
    ):
        await facade.list_recent(
            invalid_limit  # type: ignore[arg-type]
        )

    service.list_recent.assert_not_called()


def test_facade_rejects_non_service_dependency() -> None:
    with pytest.raises(
        TypeError
    ):
        DecisionAuditQueryFacade(
            object()  # type: ignore[arg-type]
        )


def test_facade_has_exact_public_query_methods() -> None:
    public_methods = {
        name
        for name, value
        in DecisionAuditQueryFacade.__dict__.items()
        if (
            callable(
                value
            )
            and not name.startswith(
                "_"
            )
        )
    }

    assert public_methods == {
        "get_by_event_id",
        "get_by_idempotency_key",
        "latest",
        "list_recent",
    }


def test_dto_is_frozen() -> None:
    dto = SerializedDecisionAuditDTO(
        canonical_json='{"status":"ok"}'
    )

    with pytest.raises(
        Exception
    ):
        dto.canonical_json = (  # type: ignore[misc]
            '{"status":"changed"}'
        )
