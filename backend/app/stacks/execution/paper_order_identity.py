"""Canonical request identity for simulated paper orders.

No database access, order execution, or live-broker operations.
"""

from __future__ import annotations

import hashlib
import json
import re
from uuid import UUID


class PaperOrderIdentityError(ValueError):
    """A paper-order request has invalid identity or intent."""


class PaperOrderIdentityConflict(PaperOrderIdentityError):
    """A request ID was reused for different order intent."""


def normalize_request_id(value: str) -> str:
    if not isinstance(value, str):
        raise PaperOrderIdentityError(
            "Paper-order request_id must be a UUID string"
        )

    try:
        result = str(UUID(value.strip()))
    except (ValueError, AttributeError) as exc:
        raise PaperOrderIdentityError(
            "Paper-order request_id must be a valid UUID"
        ) from exc

    return result


def normalize_order_intent(
    *,
    symbol: str,
    action: str,
) -> dict[str, str]:
    if not isinstance(symbol, str):
        raise PaperOrderIdentityError(
            "Paper-order symbol must be a string"
        )

    if not isinstance(action, str):
        raise PaperOrderIdentityError(
            "Paper-order action must be a string"
        )

    normalized_symbol = symbol.strip().upper()
    normalized_action = action.strip().lower()

    if not re.fullmatch(
        r"[A-Z0-9][A-Z0-9.\-]{0,14}",
        normalized_symbol,
    ):
        raise PaperOrderIdentityError(
            "Invalid paper-order symbol"
        )

    if normalized_action not in {"buy", "sell"}:
        raise PaperOrderIdentityError(
            "Unsupported paper-order action"
        )

    return {
        "symbol": normalized_symbol,
        "action": normalized_action,
    }


def fingerprint_order_intent(
    *,
    symbol: str,
    action: str,
) -> str:
    intent = normalize_order_intent(
        symbol=symbol,
        action=action,
    )

    canonical = json.dumps(
        {
            "contract": "neurovest-paper-order-intent-v1",
            **intent,
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    return hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()


def assert_matching_fingerprint(
    *,
    existing_fingerprint: str,
    incoming_fingerprint: str,
) -> None:
    if (
        not isinstance(existing_fingerprint, str)
        or not isinstance(incoming_fingerprint, str)
        or not re.fullmatch(
            r"[0-9a-f]{64}",
            existing_fingerprint,
        )
        or not re.fullmatch(
            r"[0-9a-f]{64}",
            incoming_fingerprint,
        )
    ):
        raise PaperOrderIdentityError(
            "Paper-order fingerprint is invalid"
        )

    if existing_fingerprint != incoming_fingerprint:
        raise PaperOrderIdentityConflict(
            "Request ID already belongs to a different order"
        )
