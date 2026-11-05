from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from sqlalchemy import text


class CommitOutcome(str, Enum):
    CONFIRMED_COMMITTED = "CONFIRMED_COMMITTED"
    CONFLICT = "CONFLICT"
    NOT_OBSERVED_UNCERTAIN = "NOT_OBSERVED_UNCERTAIN"
    UNAVAILABLE_UNCERTAIN = "UNAVAILABLE_UNCERTAIN"


@dataclass(frozen=True)
class CommitReconciliation:
    outcome: CommitOutcome
    order_id: int | None = None
    retry_authorized: bool = False


def _validated_identity(
    user_id: str,
    request_id: str,
    fingerprint: str,
) -> tuple[str, str, str]:
    if not isinstance(user_id, str) or not user_id.strip():
        raise ValueError("Valid owner required")

    if not isinstance(request_id, str):
        raise ValueError("Valid request UUID required")

    canonical_id = str(UUID(request_id))

    if (
        not isinstance(fingerprint, str)
        or len(fingerprint) != 64
        or any(c not in "0123456789abcdef" for c in fingerprint)
    ):
        raise ValueError("Canonical SHA-256 fingerprint required")

    return user_id.strip(), canonical_id, fingerprint


async def reconcile_commit_outcome(
    session,
    *,
    user_id: str,
    request_id: str,
    request_fingerprint: str,
) -> CommitReconciliation:
    """
    Read-only reconciliation following an uncertain commit.

    The caller supplies an independently established, trusted
    database session. This function never opens a connection,
    commits, rolls back, or authorizes a retry.

    Absence of a row is inconclusive: the original transaction
    might still be processing or become visible later.
    """
    owner, identity, fingerprint = _validated_identity(
        user_id,
        request_id,
        request_fingerprint,
    )

    try:
        result = await session.execute(
            text(
                "SELECT id, request_fingerprint "
                "FROM order_history "
                "WHERE user_id = :owner "
                "AND request_id = :request_id"
            ),
            {
                "owner": owner,
                "request_id": identity,
            },
        )

        rows = result.mappings().all()

    except Exception:
        return CommitReconciliation(
            CommitOutcome.UNAVAILABLE_UNCERTAIN
        )

    if not rows:
        return CommitReconciliation(
            CommitOutcome.NOT_OBSERVED_UNCERTAIN
        )

    # Ambiguous duplicate identities must fail closed.
    if len(rows) != 1:
        return CommitReconciliation(CommitOutcome.CONFLICT)

    row = rows[0]

    if row["request_fingerprint"] != fingerprint:
        return CommitReconciliation(CommitOutcome.CONFLICT)

    try:
        order_id = int(row["id"])
    except (ValueError, TypeError, OverflowError):
        return CommitReconciliation(CommitOutcome.CONFLICT)

    if order_id <= 0:
        return CommitReconciliation(CommitOutcome.CONFLICT)

    return CommitReconciliation(
        CommitOutcome.CONFIRMED_COMMITTED,
        order_id=order_id,
    )
