"""
Read-only decision-audit query facade.

This facade is the approved production consumer boundary for decision-audit
reads. It delegates exclusively to DecisionAuditService and returns immutable,
serialized DTOs.

It owns no repository, ORM model, SQLAlchemy session, transaction, append,
mutation, sequence, hash, API route, broker execution, or live-trading
capability.
"""

from __future__ import annotations

import inspect
import json
from dataclasses import asdict, dataclass, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Mapping
from uuid import UUID

from backend.app.stacks.journal_ledger.decision_audit_service import (
    DecisionAuditService,
)


@dataclass(
    frozen=True,
    slots=True,
)
class SerializedDecisionAuditDTO:
    """
    Immutable serialized decision-audit record.

    The canonical JSON string is the stored public representation. A caller may
    request a fresh dictionary copy through ``to_dict`` without gaining access
    to an ORM model, repository record, or database session.
    """

    canonical_json: str

    def to_dict(
        self,
    ) -> dict[str, Any]:
        value = json.loads(
            self.canonical_json
        )

        if not isinstance(
            value,
            dict,
        ):
            raise TypeError(
                "serialized decision audit DTO "
                "must contain a JSON object"
            )

        return value


class DecisionAuditQueryFacade:
    """
    Approved read-only decision-audit consumer facade.
    """

    __slots__ = (
        "_audit_service",
    )

    def __init__(
        self,
        audit_service: DecisionAuditService,
    ) -> None:
        if not isinstance(
            audit_service,
            DecisionAuditService,
        ):
            raise TypeError(
                "audit_service must be a "
                "DecisionAuditService"
            )

        self._audit_service = (
            audit_service
        )

    async def get_by_event_id(
        self,
        event_id: UUID,
    ) -> SerializedDecisionAuditDTO | None:
        record = await self._await_result(
            self._audit_service.get_by_event_id(
                event_id
            )
        )

        return self._serialize_optional(
            record
        )

    async def get_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> SerializedDecisionAuditDTO | None:
        if not isinstance(
            idempotency_key,
            str,
        ):
            raise TypeError(
                "idempotency_key must be a string"
            )

        normalized_key = (
            idempotency_key.strip()
        )

        if not normalized_key:
            raise ValueError(
                "idempotency_key must not be empty"
            )

        record = await self._await_result(
            self._audit_service.get_by_idempotency_key(
                normalized_key
            )
        )

        return self._serialize_optional(
            record
        )

    async def latest(
        self,
    ) -> SerializedDecisionAuditDTO | None:
        record = await self._await_result(
            self._audit_service.latest()
        )

        return self._serialize_optional(
            record
        )

    async def list_recent(
        self,
        limit: int = 100,
    ) -> tuple[
        SerializedDecisionAuditDTO,
        ...,
    ]:
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

        records = await self._await_result(
            self._audit_service.list_recent(
                limit
            )
        )

        if records is None:
            return ()

        if isinstance(
            records,
            (
                str,
                bytes,
                bytearray,
                Mapping,
            ),
        ):
            raise TypeError(
                "list_recent must return an "
                "iterable of records"
            )

        return tuple(
            self._serialize_record(
                record
            )
            for record in records
        )

    @staticmethod
    async def _await_result(
        value: Any,
    ) -> Any:
        if inspect.isawaitable(
            value
        ):
            return await value

        return value

    @classmethod
    def _serialize_optional(
        cls,
        record: Any,
    ) -> SerializedDecisionAuditDTO | None:
        if record is None:
            return None

        return cls._serialize_record(
            record
        )

    @classmethod
    def _serialize_record(
        cls,
        record: Any,
    ) -> SerializedDecisionAuditDTO:
        normalized = cls._normalize_json_value(
            record
        )

        if not isinstance(
            normalized,
            dict,
        ):
            raise TypeError(
                "decision audit service must return "
                "an object-shaped record"
            )

        canonical_json = json.dumps(
            normalized,
            ensure_ascii=False,
            allow_nan=False,
            separators=(
                ",",
                ":",
            ),
            sort_keys=True,
        )

        return SerializedDecisionAuditDTO(
            canonical_json=canonical_json
        )

    @classmethod
    def _normalize_json_value(
        cls,
        value: Any,
    ) -> Any:
        if value is None or isinstance(
            value,
            (
                str,
                int,
                bool,
            ),
        ):
            return value

        if isinstance(
            value,
            float,
        ):
            if value != value or value in {
                float("inf"),
                float("-inf"),
            }:
                raise ValueError(
                    "non-finite float is not "
                    "JSON serializable"
                )

            return value

        if isinstance(
            value,
            Decimal,
        ):
            return str(
                value
            )

        if isinstance(
            value,
            UUID,
        ):
            return str(
                value
            )

        if isinstance(
            value,
            (
                datetime,
                date,
            ),
        ):
            return value.isoformat()

        if isinstance(
            value,
            Enum,
        ):
            return cls._normalize_json_value(
                value.value
            )

        if is_dataclass(
            value
        ):
            return cls._normalize_json_value(
                asdict(
                    value
                )
            )

        model_dump = getattr(
            value,
            "model_dump",
            None,
        )

        if callable(
            model_dump
        ):
            return cls._normalize_json_value(
                model_dump(
                    mode="json"
                )
            )

        to_dict = getattr(
            value,
            "to_dict",
            None,
        )

        if callable(
            to_dict
        ):
            return cls._normalize_json_value(
                to_dict()
            )

        if isinstance(
            value,
            Mapping,
        ):
            normalized = {}

            for key, item in value.items():
                if not isinstance(
                    key,
                    str,
                ):
                    raise TypeError(
                        "decision audit mapping keys "
                        "must be strings"
                    )

                normalized[key] = (
                    cls._normalize_json_value(
                        item
                    )
                )

            return normalized

        if isinstance(
            value,
            (
                list,
                tuple,
            ),
        ):
            return [
                cls._normalize_json_value(
                    item
                )
                for item in value
            ]

        raise TypeError(
            "unsupported decision audit value: "
            f"{type(value).__name__}"
        )


__all__ = [
    "DecisionAuditQueryFacade",
    "SerializedDecisionAuditDTO",
]
