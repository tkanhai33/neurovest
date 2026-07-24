from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from backend.app.stacks.journal_ledger.decision_event_contract import (
    DecisionEventDraft,
    DecisionEventError,
    DecisionEventType,
    DecisionOutcome,
    PersistedDecisionEvent,
    verify_chain_link,
)


EVENT_ID = UUID(
    "00000000-0000-0000-0000-000000000001"
)

CORRELATION_ID = UUID(
    "00000000-0000-0000-0000-000000000002"
)

SECOND_EVENT_ID = UUID(
    "00000000-0000-0000-0000-000000000003"
)

OCCURRED_AT = datetime(
    2026,
    7,
    10,
    18,
    0,
    tzinfo=UTC,
)


def make_draft(
    *,
    event_id: UUID = EVENT_ID,
    idempotency_key: str = "decision:AAPL:001",
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
        symbol="aapl",
        confidence=0.92,
        reason="Risk threshold exceeded",
        payload={
            "threshold": 0.10,
            "observed": 0.14,
            "checks": [
                "position_limit",
                "drawdown_limit",
            ],
        },
    )


def test_draft_normalizes_and_freezes_contract() -> None:
    draft = make_draft()

    assert draft.symbol == "AAPL"
    assert draft.confidence == 0.92

    with pytest.raises(
        FrozenInstanceError,
    ):
        draft.symbol = "MSFT"  # type: ignore[misc]

    with pytest.raises(
        TypeError,
    ):
        draft.payload[
            "threshold"
        ] = 0.20  # type: ignore[index]


def test_canonical_hash_is_deterministic() -> None:
    first = make_draft()
    second = make_draft()

    assert (
        first.content_hash()
        == second.content_hash()
    )

    assert len(
        first.content_hash()
    ) == 64


def test_payload_key_order_does_not_change_hash() -> None:
    first = DecisionEventDraft(
        event_id=EVENT_ID,
        idempotency_key="same-key",
        event_type=(
            DecisionEventType.STRATEGY_DECISION
        ),
        outcome=(
            DecisionOutcome.PROPOSED
        ),
        occurred_at=OCCURRED_AT,
        actor="strategy-engine",
        source="strategy.stack",
        correlation_id=CORRELATION_ID,
        payload={
            "a": 1,
            "b": 2,
        },
    )

    second = DecisionEventDraft(
        event_id=EVENT_ID,
        idempotency_key="same-key",
        event_type=(
            DecisionEventType.STRATEGY_DECISION
        ),
        outcome=(
            DecisionOutcome.PROPOSED
        ),
        occurred_at=OCCURRED_AT,
        actor="strategy-engine",
        source="strategy.stack",
        correlation_id=CORRELATION_ID,
        payload={
            "b": 2,
            "a": 1,
        },
    )

    assert (
        first.content_hash()
        == second.content_hash()
    )


def test_naive_datetime_is_rejected() -> None:
    with pytest.raises(
        DecisionEventError,
        match="timezone-aware",
    ):
        DecisionEventDraft(
            event_id=EVENT_ID,
            idempotency_key="invalid-time",
            event_type=(
                DecisionEventType.SYSTEM_SAFETY_EVENT
            ),
            outcome=(
                DecisionOutcome.OBSERVED
            ),
            occurred_at=datetime(
                2026,
                7,
                10,
                18,
                0,
            ),
            actor="system",
            source="runtime",
            correlation_id=CORRELATION_ID,
        )


def test_invalid_confidence_is_rejected() -> None:
    with pytest.raises(
        DecisionEventError,
        match="between 0 and 1",
    ):
        DecisionEventDraft(
            event_id=EVENT_ID,
            idempotency_key="invalid-confidence",
            event_type=(
                DecisionEventType.RISK_DECISION
            ),
            outcome=(
                DecisionOutcome.REJECTED
            ),
            occurred_at=OCCURRED_AT,
            actor="risk-engine",
            source="risk.stack",
            correlation_id=CORRELATION_ID,
            confidence=1.5,
        )


def test_first_persisted_event_requires_no_previous_hash() -> None:
    draft = make_draft()

    event = PersistedDecisionEvent(
        sequence_number=1,
        recorded_at=(
            OCCURRED_AT
            + timedelta(
                seconds=1
            )
        ),
        previous_hash=None,
        content_hash=(
            draft.content_hash()
        ),
        draft=draft,
    )

    assert event.sequence_number == 1


def test_non_first_event_requires_previous_hash() -> None:
    draft = make_draft(
        event_id=SECOND_EVENT_ID,
        idempotency_key="decision:AAPL:002",
    )

    with pytest.raises(
        DecisionEventError,
        match="must contain previous_hash",
    ):
        PersistedDecisionEvent(
            sequence_number=2,
            recorded_at=(
                OCCURRED_AT
                + timedelta(
                    seconds=1
                )
            ),
            previous_hash=None,
            content_hash=(
                draft.content_hash()
            ),
            draft=draft,
        )


def test_content_hash_mismatch_is_rejected() -> None:
    draft = make_draft()

    with pytest.raises(
        DecisionEventError,
        match="does not match",
    ):
        PersistedDecisionEvent(
            sequence_number=1,
            recorded_at=(
                OCCURRED_AT
                + timedelta(
                    seconds=1
                )
            ),
            previous_hash=None,
            content_hash=(
                "0"
                * 64
            ),
            draft=draft,
        )


def test_chain_link_requires_contiguous_sequence_and_hash() -> None:
    first_draft = make_draft()

    first = PersistedDecisionEvent(
        sequence_number=1,
        recorded_at=(
            OCCURRED_AT
            + timedelta(
                seconds=1
            )
        ),
        previous_hash=None,
        content_hash=(
            first_draft.content_hash()
        ),
        draft=first_draft,
    )

    second_draft = make_draft(
        event_id=SECOND_EVENT_ID,
        idempotency_key="decision:AAPL:002",
    )

    second = PersistedDecisionEvent(
        sequence_number=2,
        recorded_at=(
            OCCURRED_AT
            + timedelta(
                seconds=2
            )
        ),
        previous_hash=(
            first.content_hash
        ),
        content_hash=(
            second_draft.content_hash()
        ),
        draft=second_draft,
    )

    verify_chain_link(
        first,
        second,
    )
