from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest

from backend.app.stacks.journal_ledger.decision_audit_query_facade import (
    DecisionAuditQueryFacade,
)
from backend.app.stacks.journal_ledger.decision_audit_service import (
    DecisionAuditService,
)


@dataclass(
    frozen=True,
    slots=True,
)
class ValidRecord:
    event_id: UUID
    idempotency_key: str
    payload: dict[str, object]


class UnsupportedRecord:
    pass


def build_service() -> AsyncMock:
    return AsyncMock(
        spec=DecisionAuditService
    )


def build_record() -> ValidRecord:
    return ValidRecord(
        event_id=uuid4(),
        idempotency_key="stage8d-key",
        payload={
            "decision": "HOLD",
        },
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "method_name",
        "arguments",
    ),
    [
        (
            "get_by_event_id",
            lambda: (
                uuid4(),
            ),
        ),
        (
            "get_by_idempotency_key",
            lambda: (
                "stage8d-key",
            ),
        ),
        (
            "latest",
            lambda: (),
        ),
        (
            "list_recent",
            lambda: (
                25,
            ),
        ),
    ],
)
async def test_service_failures_propagate_without_fallback_data(
    method_name: str,
    arguments: object,
) -> None:
    service = build_service()

    failure = RuntimeError(
        f"{method_name} unavailable"
    )

    service_method = getattr(
        service,
        method_name,
    )

    service_method.side_effect = failure

    facade = DecisionAuditQueryFacade(
        service
    )

    argument_factory = arguments

    with pytest.raises(
        RuntimeError,
        match="unavailable",
    ) as captured:
        await getattr(
            facade,
            method_name,
        )(
            *argument_factory()
        )

    assert captured.value is failure

    service_method.assert_awaited_once()


@pytest.mark.asyncio
async def test_blank_idempotency_key_fails_before_service_call() -> None:
    service = build_service()

    facade = DecisionAuditQueryFacade(
        service
    )

    with pytest.raises(
        ValueError,
        match="must not be empty",
    ):
        await facade.get_by_idempotency_key(
            "   "
        )

    service.get_by_idempotency_key.assert_not_called()


@pytest.mark.asyncio
async def test_non_string_idempotency_key_fails_before_service_call() -> None:
    service = build_service()

    facade = DecisionAuditQueryFacade(
        service
    )

    with pytest.raises(
        TypeError,
        match="must be a string",
    ):
        await facade.get_by_idempotency_key(
            123  # type: ignore[arg-type]
        )

    service.get_by_idempotency_key.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "invalid_limit",
    [
        0,
        -1,
        1001,
        True,
        10.5,
        "10",
        None,
    ],
)
async def test_invalid_list_limit_fails_before_service_call(
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


@pytest.mark.asyncio
async def test_unsupported_record_type_fails_closed() -> None:
    service = build_service()

    service.latest.return_value = (
        UnsupportedRecord()
    )

    facade = DecisionAuditQueryFacade(
        service
    )

    with pytest.raises(
        TypeError,
        match="unsupported decision audit value",
    ):
        await facade.latest()

    service.latest.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_scalar_service_record_fails_closed() -> None:
    service = build_service()

    service.latest.return_value = (
        "not-an-object"
    )

    facade = DecisionAuditQueryFacade(
        service
    )

    with pytest.raises(
        TypeError,
        match="object-shaped record",
    ):
        await facade.latest()


@pytest.mark.asyncio
async def test_mapping_with_non_string_key_fails_closed() -> None:
    service = build_service()

    service.latest.return_value = {
        1: "invalid-key",
    }

    facade = DecisionAuditQueryFacade(
        service
    )

    with pytest.raises(
        TypeError,
        match="mapping keys must be strings",
    ):
        await facade.latest()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "invalid_float",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
async def test_non_finite_float_fails_closed(
    invalid_float: float,
) -> None:
    service = build_service()

    service.latest.return_value = {
        "confidence": invalid_float,
    }

    facade = DecisionAuditQueryFacade(
        service
    )

    with pytest.raises(
        ValueError,
        match="non-finite float",
    ):
        await facade.latest()


@pytest.mark.asyncio
async def test_list_recent_rejects_mapping_as_collection() -> None:
    service = build_service()

    service.list_recent.return_value = {
        "event": build_record(),
    }

    facade = DecisionAuditQueryFacade(
        service
    )

    with pytest.raises(
        TypeError,
        match="iterable of records",
    ):
        await facade.list_recent(
            10
        )


@pytest.mark.asyncio
async def test_list_recent_does_not_return_partial_collection() -> None:
    service = build_service()

    service.list_recent.return_value = [
        build_record(),
        UnsupportedRecord(),
    ]

    facade = DecisionAuditQueryFacade(
        service
    )

    with pytest.raises(
        TypeError,
        match="unsupported decision audit value",
    ):
        await facade.list_recent(
            10
        )


@pytest.mark.asyncio
async def test_none_reads_remain_explicit_none() -> None:
    service = build_service()

    service.get_by_event_id.return_value = None
    service.get_by_idempotency_key.return_value = None
    service.latest.return_value = None
    service.list_recent.return_value = None

    facade = DecisionAuditQueryFacade(
        service
    )

    assert (
        await facade.get_by_event_id(
            uuid4()
        )
        is None
    )

    assert (
        await facade.get_by_idempotency_key(
            "missing-key"
        )
        is None
    )

    assert await facade.latest() is None
    assert await facade.list_recent(10) == ()


@pytest.mark.asyncio
async def test_valid_result_remains_serialized_after_failure_tests() -> None:
    service = build_service()

    record = build_record()

    service.latest.return_value = record

    facade = DecisionAuditQueryFacade(
        service
    )

    result = await facade.latest()

    assert result is not None

    payload = result.to_dict()

    assert payload[
        "event_id"
    ] == str(
        record.event_id
    )

    assert payload[
        "payload"
    ]["decision"] == "HOLD"
