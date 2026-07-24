"""
Canonical append-only decision-event contract.

This module defines provider-independent, persistence-independent event
contracts for decisions produced by NeuroVest.

The contract does not:

- define an ORM model
- create or migrate a table
- open a database session
- write a record
- expose an API route
- enable broker execution
- enable live trading

Persistence implementation is deferred until the contract and transaction
semantics are frozen.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Mapping
from uuid import UUID


_HEX_64_PATTERN = re.compile(
    r"^[0-9a-f]{64}$"
)

_EVENT_VERSION = 1


class DecisionEventError(
    ValueError,
):
    """Raised when a decision event violates the canonical contract."""


class DecisionEventType(
    StrEnum,
):
    """
    Immutable categories of decision evidence.

    These categories describe decisions and safety outcomes only.
    They do not represent broker orders or authorization to trade.
    """

    STRATEGY_DECISION = "strategy_decision"
    RISK_DECISION = "risk_decision"
    EXECUTION_INTENT = "execution_intent"
    EXECUTION_BLOCKED = "execution_blocked"
    HUMAN_APPROVAL = "human_approval"
    HUMAN_REJECTION = "human_rejection"
    SYSTEM_SAFETY_EVENT = "system_safety_event"


class DecisionOutcome(
    StrEnum,
):
    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"
    BLOCKED = "blocked"
    OBSERVED = "observed"


def require_non_empty(
    value: str,
    *,
    field_name: str,
) -> str:
    if not isinstance(
        value,
        str,
    ):
        raise DecisionEventError(
            f"{field_name} must be a string"
        )

    normalized = value.strip()

    if not normalized:
        raise DecisionEventError(
            f"{field_name} must not be empty"
        )

    return normalized


def require_aware_utc(
    value: datetime,
    *,
    field_name: str,
) -> datetime:
    if not isinstance(
        value,
        datetime,
    ):
        raise DecisionEventError(
            f"{field_name} must be a datetime"
        )

    if (
        value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise DecisionEventError(
            f"{field_name} must be timezone-aware"
        )

    return value.astimezone(
        UTC
    )


def require_optional_hash(
    value: str | None,
    *,
    field_name: str,
) -> str | None:
    if value is None:
        return None

    normalized = value.strip().lower()

    if not _HEX_64_PATTERN.fullmatch(
        normalized
    ):
        raise DecisionEventError(
            f"{field_name} must be a lowercase SHA-256 hash"
        )

    return normalized


def normalize_symbol(
    value: str | None,
) -> str | None:
    if value is None:
        return None

    normalized = require_non_empty(
        value,
        field_name="symbol",
    ).upper()

    if len(
        normalized
    ) > 32:
        raise DecisionEventError(
            "symbol exceeds 32 characters"
        )

    return normalized


def normalize_confidence(
    value: float | None,
) -> float | None:
    if value is None:
        return None

    normalized = float(
        value
    )

    if not math.isfinite(
        normalized
    ):
        raise DecisionEventError(
            "confidence must be finite"
        )

    if not (
        0.0
        <= normalized
        <= 1.0
    ):
        raise DecisionEventError(
            "confidence must be between 0 and 1"
        )

    return normalized


def canonicalize_value(
    value: Any,
) -> Any:
    if value is None:
        return None

    if isinstance(
        value,
        (
            str,
            bool,
            int,
        ),
    ):
        return value

    if isinstance(
        value,
        float,
    ):
        if not math.isfinite(
            value
        ):
            raise DecisionEventError(
                "payload floats must be finite"
            )

        return value

    if isinstance(
        value,
        datetime,
    ):
        return require_aware_utc(
            value,
            field_name="payload datetime",
        ).isoformat()

    if isinstance(
        value,
        UUID,
    ):
        return str(
            value
        )

    if isinstance(
        value,
        StrEnum,
    ):
        return value.value

    if isinstance(
        value,
        Mapping,
    ):
        return {
            str(
                key
            ): canonicalize_value(
                nested
            )
            for key, nested
            in sorted(
                value.items(),
                key=lambda item: str(
                    item[0]
                ),
            )
        }

    if isinstance(
        value,
        (
            tuple,
            list,
        ),
    ):
        return [
            canonicalize_value(
                nested
            )
            for nested in value
        ]

    raise DecisionEventError(
        "payload contains unsupported value type: "
        f"{type(value).__name__}"
    )


def freeze_payload(
    payload: Mapping[str, Any],
) -> Mapping[str, Any]:
    canonical = canonicalize_value(
        payload
    )

    if not isinstance(
        canonical,
        dict,
    ):
        raise DecisionEventError(
            "payload must be a mapping"
        )

    return MappingProxyType(
        canonical
    )


def canonical_json(
    value: Mapping[str, Any],
) -> str:
    canonical = canonicalize_value(
        value
    )

    return json.dumps(
        canonical,
        ensure_ascii=False,
        allow_nan=False,
        separators=(
            ",",
            ":",
        ),
        sort_keys=True,
    )


def sha256_text(
    value: str,
) -> str:
    return hashlib.sha256(
        value.encode(
            "utf-8"
        )
    ).hexdigest()


@dataclass(
    frozen=True,
    slots=True,
)
class DecisionEventDraft:
    """
    Proposed event before persistence assigns a sequence number.

    `event_id` and `idempotency_key` must be generated by the caller.
    Persistence must reject duplicate values rather than update an
    existing event.
    """

    event_id: UUID
    idempotency_key: str
    event_type: DecisionEventType
    outcome: DecisionOutcome
    occurred_at: datetime
    actor: str
    source: str
    correlation_id: UUID
    causation_id: UUID | None = None
    symbol: str | None = None
    confidence: float | None = None
    reason: str | None = None
    payload: Mapping[str, Any] = MappingProxyType(
        {}
    )

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "idempotency_key",
            require_non_empty(
                self.idempotency_key,
                field_name="idempotency_key",
            ),
        )

        object.__setattr__(
            self,
            "actor",
            require_non_empty(
                self.actor,
                field_name="actor",
            ),
        )

        object.__setattr__(
            self,
            "source",
            require_non_empty(
                self.source,
                field_name="source",
            ),
        )

        object.__setattr__(
            self,
            "occurred_at",
            require_aware_utc(
                self.occurred_at,
                field_name="occurred_at",
            ),
        )

        object.__setattr__(
            self,
            "symbol",
            normalize_symbol(
                self.symbol
            ),
        )

        object.__setattr__(
            self,
            "confidence",
            normalize_confidence(
                self.confidence
            ),
        )

        if self.reason is not None:
            object.__setattr__(
                self,
                "reason",
                require_non_empty(
                    self.reason,
                    field_name="reason",
                ),
            )

        object.__setattr__(
            self,
            "payload",
            freeze_payload(
                self.payload
            ),
        )

    def canonical_content(
        self,
    ) -> dict[str, Any]:
        return {
            "version": _EVENT_VERSION,
            "event_id": str(
                self.event_id
            ),
            "idempotency_key": (
                self.idempotency_key
            ),
            "event_type": (
                self.event_type.value
            ),
            "outcome": (
                self.outcome.value
            ),
            "occurred_at": (
                self.occurred_at.isoformat()
            ),
            "actor": self.actor,
            "source": self.source,
            "correlation_id": str(
                self.correlation_id
            ),
            "causation_id": (
                str(
                    self.causation_id
                )
                if self.causation_id
                else None
            ),
            "symbol": self.symbol,
            "confidence": self.confidence,
            "reason": self.reason,
            "payload": dict(
                self.payload
            ),
        }

    def content_hash(
        self,
    ) -> str:
        return sha256_text(
            canonical_json(
                self.canonical_content()
            )
        )


@dataclass(
    frozen=True,
    slots=True,
)
class PersistedDecisionEvent:
    """
    Persisted immutable decision event.

    Sequence numbers are monotonic within the canonical event stream.
    The first event has no previous hash. Every later event must link to
    the content hash of the previous persisted event.
    """

    sequence_number: int
    recorded_at: datetime
    previous_hash: str | None
    content_hash: str
    draft: DecisionEventDraft

    def __post_init__(
        self,
    ) -> None:
        if (
            not isinstance(
                self.sequence_number,
                int,
            )
            or isinstance(
                self.sequence_number,
                bool,
            )
            or self.sequence_number < 1
        ):
            raise DecisionEventError(
                "sequence_number must be a positive integer"
            )

        object.__setattr__(
            self,
            "recorded_at",
            require_aware_utc(
                self.recorded_at,
                field_name="recorded_at",
            ),
        )

        object.__setattr__(
            self,
            "previous_hash",
            require_optional_hash(
                self.previous_hash,
                field_name="previous_hash",
            ),
        )

        object.__setattr__(
            self,
            "content_hash",
            require_optional_hash(
                self.content_hash,
                field_name="content_hash",
            ),
        )

        expected_hash = (
            self.draft.content_hash()
        )

        if self.content_hash != expected_hash:
            raise DecisionEventError(
                "content_hash does not match canonical event content"
            )

        if (
            self.sequence_number == 1
            and self.previous_hash is not None
        ):
            raise DecisionEventError(
                "first event must not have a previous_hash"
            )

        if (
            self.sequence_number > 1
            and self.previous_hash is None
        ):
            raise DecisionEventError(
                "non-first event must contain previous_hash"
            )

        if (
            self.recorded_at
            < self.draft.occurred_at
        ):
            raise DecisionEventError(
                "recorded_at must not precede occurred_at"
            )


def verify_chain_link(
    previous: PersistedDecisionEvent,
    current: PersistedDecisionEvent,
) -> None:
    if (
        current.sequence_number
        != previous.sequence_number
        + 1
    ):
        raise DecisionEventError(
            "decision-event sequence is not contiguous"
        )

    if (
        current.previous_hash
        != previous.content_hash
    ):
        raise DecisionEventError(
            "decision-event previous_hash does not match"
        )
