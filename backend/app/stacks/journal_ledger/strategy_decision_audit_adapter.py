"""
Controlled asynchronous strategy-decision audit adapter.

Ownership boundaries:

- The strategy engine remains synchronous and database-free.
- This adapter calls the synchronous strategy producer outside the
  event loop through asyncio.to_thread().
- This adapter constructs DecisionEventDraft.
- DecisionAuditService is the only persistence dependency.
- The adapter does not import or call DecisionEventRepository.
- The adapter does not commit, flush, allocate sequence numbers,
  calculate chain linkage, or construct persistence hashes.
- The adapter does not submit orders or enable execution.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from backend.app.stacks.journal_ledger.decision_audit_service import (
    DecisionAuditService,
)
from backend.app.stacks.journal_ledger.decision_event_contract import (
    DecisionEventDraft,
    DecisionEventType,
    DecisionOutcome,
    PersistedDecisionEvent,
)
from backend.app.stacks.strategy.engine import (
    generate_strategy_decision,
)


StrategyDecisionEnvelope = dict[str, Any]

StrategyDecisionProducer = Callable[
    [
        str,
        list[dict] | None,
    ],
    StrategyDecisionEnvelope,
]


@dataclass(
    frozen=True,
    slots=True,
)
class AuditedStrategyDecision:
    """
    One strategy decision and its immutable persisted audit identity.
    """

    envelope: Mapping[str, Any]
    audit_event: PersistedDecisionEvent


class StrategyDecisionAuditAdapter:
    """
    Bridge the synchronous strategy producer to append-only auditing.

    This adapter intentionally exposes no update, delete, replace,
    merge, purge, truncate, order, broker, or execution operation.
    """

    def __init__(
        self,
        audit_service: DecisionAuditService,
        *,
        producer: StrategyDecisionProducer = (
            generate_strategy_decision
        ),
    ) -> None:
        if not isinstance(
            audit_service,
            DecisionAuditService,
        ):
            raise TypeError(
                "audit_service must be a DecisionAuditService"
            )

        if not callable(
            producer
        ):
            raise TypeError(
                "producer must be callable"
            )

        self._audit_service = (
            audit_service
        )

        self._producer = producer

    async def produce_and_audit(
        self,
        symbol: str,
        *,
        idempotency_key: str,
        correlation_id: UUID,
        actor: str = "neuro",
        source: str = (
            "backend.app.stacks.strategy.engine."
            "generate_strategy_decision"
        ),
        event_id: UUID | None = None,
        causation_id: UUID | None = None,
        occurred_at: datetime | None = None,
        replay_bars: list[dict] | None = None,
        recorded_at: datetime | None = None,
    ) -> AuditedStrategyDecision:
        """
        Produce one strategy decision and append one audit event.

        Idempotency is caller-controlled through `idempotency_key`.
        Persistence assigns sequence numbers and hash-chain linkage.
        """

        normalized_symbol = self._require_text(
            symbol,
            field_name="symbol",
        ).upper()

        normalized_idempotency_key = (
            self._require_text(
                idempotency_key,
                field_name="idempotency_key",
            )
        )

        normalized_actor = self._require_text(
            actor,
            field_name="actor",
        )

        normalized_source = self._require_text(
            source,
            field_name="source",
        )

        if not isinstance(
            correlation_id,
            UUID,
        ):
            raise TypeError(
                "correlation_id must be a UUID"
            )

        effective_event_id = (
            event_id
            if event_id is not None
            else uuid4()
        )

        if not isinstance(
            effective_event_id,
            UUID,
        ):
            raise TypeError(
                "event_id must be a UUID"
            )

        if (
            causation_id is not None
            and not isinstance(
                causation_id,
                UUID,
            )
        ):
            raise TypeError(
                "causation_id must be a UUID or None"
            )

        effective_occurred_at = (
            occurred_at
            if occurred_at is not None
            else datetime.now(
                UTC
            )
        )

        effective_occurred_at = (
            self._require_aware_utc(
                effective_occurred_at,
                field_name="occurred_at",
            )
        )

        if recorded_at is not None:
            recorded_at = (
                self._require_aware_utc(
                    recorded_at,
                    field_name="recorded_at",
                )
            )

        envelope = await asyncio.to_thread(
            self._producer,
            normalized_symbol,
            replay_bars,
        )

        self._validate_envelope(
            envelope,
            expected_symbol=(
                normalized_symbol
            ),
        )

        confidence = self._normalize_confidence(
            envelope.get(
                "confidence"
            )
        )

        decision = self._require_text(
            envelope.get(
                "decision"
            ),
            field_name="decision",
        ).upper()

        signal = self._require_text(
            envelope.get(
                "signal"
            ),
            field_name="signal",
        ).lower()

        status = self._require_text(
            envelope.get(
                "status"
            ),
            field_name="status",
        )

        reason = (
            f"Strategy proposed {decision} "
            f"for {normalized_symbol}; "
            f"signal={signal}; status={status}"
        )

        draft = DecisionEventDraft(
            event_id=effective_event_id,
            idempotency_key=(
                normalized_idempotency_key
            ),
            event_type=(
                DecisionEventType
                .STRATEGY_DECISION
            ),
            outcome=(
                DecisionOutcome.PROPOSED
            ),
            occurred_at=(
                effective_occurred_at
            ),
            actor=normalized_actor,
            source=normalized_source,
            correlation_id=(
                correlation_id
            ),
            causation_id=causation_id,
            symbol=normalized_symbol,
            confidence=confidence,
            reason=reason,
            payload={
                "strategy_envelope": (
                    self._copy_json_value(
                        envelope
                    )
                ),
                "decision": decision,
                "signal": signal,
                "status": status,
            },
        )

        persisted = (
            await self._audit_service.append(
                draft,
                recorded_at=recorded_at,
            )
        )

        return AuditedStrategyDecision(
            envelope=self._copy_json_value(
                envelope
            ),
            audit_event=persisted,
        )

    @staticmethod
    def _validate_envelope(
        envelope: object,
        *,
        expected_symbol: str,
    ) -> None:
        if not isinstance(
            envelope,
            dict,
        ):
            raise TypeError(
                "strategy producer must return a dictionary"
            )

        required = {
            "status",
            "symbol",
            "signal",
            "decision",
            "confidence",
            "strategy_signal",
            "portfolio_output",
        }

        missing = sorted(
            required - set(
                envelope
            )
        )

        if missing:
            raise ValueError(
                "strategy envelope missing fields: "
                + ", ".join(
                    missing
                )
            )

        symbol = envelope.get(
            "symbol"
        )

        if (
            not isinstance(
                symbol,
                str,
            )
            or symbol.strip().upper()
            != expected_symbol
        ):
            raise ValueError(
                "strategy envelope symbol does not "
                "match the requested symbol"
            )

        if not isinstance(
            envelope.get(
                "signal"
            ),
            str,
        ):
            raise TypeError(
                "strategy envelope signal must be a string"
            )

        if not isinstance(
            envelope.get(
                "strategy_signal"
            ),
            dict,
        ):
            raise TypeError(
                "strategy_signal must be a dictionary"
            )

        portfolio_output = envelope.get(
            "portfolio_output"
        )

        if (
            portfolio_output is not None
            and not isinstance(
                portfolio_output,
                dict,
            )
        ):
            raise TypeError(
                "portfolio_output must be a dictionary "
                "or None"
            )

    @staticmethod
    def _require_text(
        value: object,
        *,
        field_name: str,
    ) -> str:
        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                f"{field_name} must be a string"
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{field_name} must not be empty"
            )

        return normalized

    @staticmethod
    def _require_aware_utc(
        value: datetime,
        *,
        field_name: str,
    ) -> datetime:
        if not isinstance(
            value,
            datetime,
        ):
            raise TypeError(
                f"{field_name} must be a datetime"
            )

        if (
            value.tzinfo is None
            or value.utcoffset() is None
        ):
            raise ValueError(
                f"{field_name} must be timezone-aware"
            )

        return value.astimezone(
            UTC
        )

    @staticmethod
    def _normalize_confidence(
        value: object,
    ) -> float | None:
        if value is None:
            return None

        if not isinstance(
            value,
            (
                int,
                float,
            ),
        ):
            raise TypeError(
                "strategy envelope confidence must "
                "be numeric or None"
            )

        confidence = float(
            value
        )

        if not 0.0 <= confidence <= 1.0:
            raise ValueError(
                "strategy envelope confidence must "
                "be between 0.0 and 1.0"
            )

        return confidence

    @classmethod
    def _copy_json_value(
        cls,
        value: Any,
    ) -> Any:
        if isinstance(
            value,
            dict,
        ):
            return {
                str(
                    key
                ): cls._copy_json_value(
                    item
                )
                for key, item
                in value.items()
            }

        if isinstance(
            value,
            (
                list,
                tuple,
            ),
        ):
            return [
                cls._copy_json_value(
                    item
                )
                for item in value
            ]

        if isinstance(
            value,
            (
                str,
                int,
                float,
                bool,
            ),
        ) or value is None:
            return value

        raise TypeError(
            "strategy envelope contains a "
            "non-JSON-compatible value: "
            f"{type(value).__name__}"
        )
