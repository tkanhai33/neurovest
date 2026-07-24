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
    DecisionEventType,
    DecisionOutcome,
)
from backend.app.stacks.journal_ledger.strategy_decision_audit_adapter import (
    StrategyDecisionAuditAdapter,
)


def build_envelope(
    symbol: str = "AAPL",
) -> dict:
    strategy_signal = {
        "status": "ok",
        "symbol": symbol,
        "action": "buy",
        "decision": "BUY",
        "rsi": 42.0,
        "confidence": 0.75,
    }

    return {
        "status": "rebalanced",
        "symbol": symbol,
        "signal": "buy",
        "decision": "BUY",
        "confidence": 0.75,
        "strategy_signal": strategy_signal,
        "portfolio_output": {
            "symbol": symbol,
            "signal": "buy",
            "status": "rebalanced",
        },
    }


@pytest.mark.asyncio
async def test_produce_and_audit_delegates_to_service() -> None:
    persisted = object()

    service = AsyncMock(
        spec=DecisionAuditService
    )

    service.append.return_value = (
        persisted
    )

    producer = AsyncMock()

    # The production adapter calls a synchronous producer inside
    # asyncio.to_thread, so tests use a normal callable.
    def synchronous_producer(
        symbol: str,
        replay_bars: list[dict] | None,
    ) -> dict:
        assert symbol == "AAPL"
        assert replay_bars == [
            {
                "close": 100.0,
            }
        ]

        return build_envelope(
            symbol
        )

    adapter = StrategyDecisionAuditAdapter(
        service,
        producer=synchronous_producer,
    )

    occurred_at = datetime(
        2026,
        7,
        10,
        20,
        0,
        tzinfo=UTC,
    )

    recorded_at = datetime(
        2026,
        7,
        10,
        20,
        1,
        tzinfo=UTC,
    )

    event_id = uuid4()
    correlation_id = uuid4()
    causation_id = uuid4()

    result = await adapter.produce_and_audit(
        "aapl",
        idempotency_key=(
            "stage7f:test:aapl:1"
        ),
        correlation_id=correlation_id,
        actor="neuro",
        source="strategy.test",
        event_id=event_id,
        causation_id=causation_id,
        occurred_at=occurred_at,
        recorded_at=recorded_at,
        replay_bars=[
            {
                "close": 100.0,
            }
        ],
    )

    assert result.audit_event is (
        persisted
    )

    assert result.envelope[
        "symbol"
    ] == "AAPL"

    service.append.assert_awaited_once()

    positional = service.append.await_args.args
    keywords = service.append.await_args.kwargs

    assert len(
        positional
    ) == 1

    draft = positional[
        0
    ]

    assert isinstance(
        draft,
        DecisionEventDraft,
    )

    assert draft.event_id == event_id

    assert draft.idempotency_key == (
        "stage7f:test:aapl:1"
    )

    assert draft.event_type is (
        DecisionEventType
        .STRATEGY_DECISION
    )

    assert draft.outcome is (
        DecisionOutcome.PROPOSED
    )

    assert draft.occurred_at == (
        occurred_at
    )

    assert draft.actor == "neuro"
    assert draft.source == "strategy.test"
    assert draft.correlation_id == (
        correlation_id
    )
    assert draft.causation_id == (
        causation_id
    )
    assert draft.symbol == "AAPL"
    assert draft.confidence == 0.75
    assert "BUY" in (
        draft.reason
        or ""
    )

    assert draft.payload[
        "decision"
    ] == "BUY"

    assert draft.payload[
        "signal"
    ] == "buy"

    assert draft.payload[
        "strategy_envelope"
    ][
        "strategy_signal"
    ][
        "rsi"
    ] == 42.0

    assert keywords == {
        "recorded_at": recorded_at,
    }


@pytest.mark.asyncio
async def test_missing_envelope_field_fails_before_append() -> None:
    service = AsyncMock(
        spec=DecisionAuditService
    )

    def producer(
        symbol: str,
        replay_bars: list[dict] | None,
    ) -> dict:
        envelope = build_envelope(
            symbol
        )

        del envelope[
            "strategy_signal"
        ]

        return envelope

    adapter = StrategyDecisionAuditAdapter(
        service,
        producer=producer,
    )

    with pytest.raises(
        ValueError,
        match="missing fields",
    ):
        await adapter.produce_and_audit(
            "AAPL",
            idempotency_key=(
                "stage7f:test:missing"
            ),
            correlation_id=uuid4(),
        )

    service.append.assert_not_awaited()


@pytest.mark.asyncio
async def test_symbol_mismatch_fails_before_append() -> None:
    service = AsyncMock(
        spec=DecisionAuditService
    )

    def producer(
        symbol: str,
        replay_bars: list[dict] | None,
    ) -> dict:
        return build_envelope(
            "MSFT"
        )

    adapter = StrategyDecisionAuditAdapter(
        service,
        producer=producer,
    )

    with pytest.raises(
        ValueError,
        match="symbol does not match",
    ):
        await adapter.produce_and_audit(
            "AAPL",
            idempotency_key=(
                "stage7f:test:mismatch"
            ),
            correlation_id=uuid4(),
        )

    service.append.assert_not_awaited()


@pytest.mark.asyncio
async def test_invalid_confidence_fails_before_append() -> None:
    service = AsyncMock(
        spec=DecisionAuditService
    )

    def producer(
        symbol: str,
        replay_bars: list[dict] | None,
    ) -> dict:
        envelope = build_envelope(
            symbol
        )

        envelope[
            "confidence"
        ] = 1.5

        return envelope

    adapter = StrategyDecisionAuditAdapter(
        service,
        producer=producer,
    )

    with pytest.raises(
        ValueError,
        match="between 0.0 and 1.0",
    ):
        await adapter.produce_and_audit(
            "AAPL",
            idempotency_key=(
                "stage7f:test:confidence"
            ),
            correlation_id=uuid4(),
        )

    service.append.assert_not_awaited()


@pytest.mark.asyncio
async def test_naive_occurred_at_is_rejected() -> None:
    service = AsyncMock(
        spec=DecisionAuditService
    )

    adapter = StrategyDecisionAuditAdapter(
        service,
        producer=(
            lambda symbol, replay_bars:
            build_envelope(
                symbol
            )
        ),
    )

    with pytest.raises(
        ValueError,
        match="timezone-aware",
    ):
        await adapter.produce_and_audit(
            "AAPL",
            idempotency_key=(
                "stage7f:test:naive"
            ),
            correlation_id=uuid4(),
            occurred_at=datetime(
                2026,
                7,
                10,
                20,
                0,
            ),
        )

    service.append.assert_not_awaited()


def test_adapter_exposes_no_mutation_or_execution_methods() -> None:
    forbidden = {
        "update",
        "delete",
        "remove",
        "replace",
        "merge",
        "purge",
        "truncate",
        "commit",
        "rollback",
        "flush",
        "submit_order",
        "place_order",
        "execute_trade",
        "execute_order",
    }

    assert forbidden.isdisjoint(
        set(
            dir(
                StrategyDecisionAuditAdapter
            )
        )
    )
