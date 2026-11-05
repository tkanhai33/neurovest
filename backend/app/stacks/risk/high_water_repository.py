from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from sqlalchemy import text

from backend.app.stacks.risk.equity_high_water import (
    HighWaterStateUnavailable,
    advance_high_water,
)


def _require_transaction(session: Any) -> None:
    if not callable(getattr(session, "in_transaction", None)):
        raise HighWaterStateUnavailable("transaction_unavailable")

    if not session.in_transaction():
        raise HighWaterStateUnavailable("transaction_required")


async def advance_persisted_high_water(
    *,
    session: Any,
    owner: str,
    currency: str,
    verified_equity: Mapping[str, object],
) -> dict:
    """
    Advance an EXISTING paper-equity high-water mark.

    Caller owns the transaction and its eventual commit.

    This function does not commit, initialize accounts,
    calculate prices, or authorize execution.

    Production integration must hold the same transaction
    serialization boundary for valuation, order authorization,
    high-water update, and ledger mutation.
    """
    if not isinstance(owner, str) or not owner.strip():
        raise HighWaterStateUnavailable("owner_unavailable")

    if (
        not isinstance(currency, str)
        or len(currency.strip()) != 3
        or not currency.strip().isascii()
        or not currency.strip().isalpha()
    ):
        raise HighWaterStateUnavailable("currency_invalid")

    if not isinstance(verified_equity, Mapping):
        raise HighWaterStateUnavailable("equity_unavailable")

    _require_transaction(session)

    normalized_owner = owner.strip()
    normalized_currency = currency.strip().upper()

    result = await session.execute(
        text("""
            SELECT
                user_id,
                currency,
                peak_equity,
                revision
            FROM paper_equity_high_water
            WHERE user_id = :owner
            FOR UPDATE
        """),
        {"owner": normalized_owner},
    )

    record = result.mappings().one_or_none()

    if record is None:
        raise HighWaterStateUnavailable(
            "persistent_high_water_missing"
        )

    if str(record["user_id"]) != normalized_owner:
        raise HighWaterStateUnavailable(
            "persistent_owner_mismatch"
        )

    if record["currency"] != normalized_currency:
        raise HighWaterStateUnavailable(
            "persistent_currency_mismatch"
        )

    transition = advance_high_water(
        owner=normalized_owner,
        verified_equity=verified_equity,
        stored_peak=record["peak_equity"],
        stored_revision=record["revision"],
    )

    if transition["peak_changed"]:
        update = await session.execute(
            text("""
                UPDATE paper_equity_high_water
                SET
                    peak_equity = :new_peak,
                    revision = :new_revision,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = :owner
                  AND revision = :previous_revision
                  AND peak_equity = :previous_peak
                RETURNING user_id, revision, peak_equity
            """),
            {
                "owner": normalized_owner,
                "new_peak": transition["new_peak"],
                "new_revision": transition["new_revision"],
                "previous_revision":
                    transition["previous_revision"],
                "previous_peak": transition["previous_peak"],
            },
        )

        changed = update.mappings().one_or_none()

        if changed is None:
            raise HighWaterStateUnavailable(
                "persistent_high_water_conflict"
            )

        if (
            str(changed["user_id"]) != normalized_owner
            or changed["revision"] != transition["new_revision"]
            or str(changed["peak_equity"])
                != transition["new_peak"]
        ):
            # Decimal values may serialize with trailing zeros.
            from decimal import Decimal
            try:
                valid_peak = (
                    Decimal(str(changed["peak_equity"]))
                    == Decimal(transition["new_peak"])
                )
            except Exception:
                valid_peak = False

            if (
                str(changed["user_id"]) != normalized_owner
                or changed["revision"] != transition["new_revision"]
                or not valid_peak
            ):
                raise HighWaterStateUnavailable(
                    "persistent_high_water_update_invalid"
                )

    return {
        **transition,
        "storage": "postgresql_transaction",
        "row_lock": "for_update",
        "persisted": False,
        "pending_transaction_commit": bool(
            transition["peak_changed"]
        ),
        "execution_authorized": False,
    }
