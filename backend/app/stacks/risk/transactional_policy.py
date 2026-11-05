from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from backend.app.stacks.risk.financial_policy import (
    FinancialPolicyUnavailable,
    evaluate_financial_policy,
)
from backend.app.stacks.risk.high_water_repository import (
    advance_persisted_high_water,
)


async def evaluate_transactional_financial_policy(
    *,
    session: Any,
    owner: str,
    currency: str,
    action: str,
    order_value: object,
    commission: object,
    verified_equity: Mapping[str, object],
    limits: Mapping[str, object],
) -> dict:
    """
    Evaluate financial policy with a locked high-water record.

    Caller must already hold the authoritative ledger
    serialization boundary, and must supply account state
    read consistently inside that same transaction.

    This function does not acquire the ledger advisory lock,
    fetch quotes, commit, or authorize execution.

    A positive policy decision is advisory until integrated
    into the complete order commit boundary.
    """
    if not isinstance(verified_equity, Mapping):
        raise FinancialPolicyUnavailable("equity_unavailable")

    if verified_equity.get("status") != "verified":
        raise FinancialPolicyUnavailable("equity_not_verified")

    if (
        not isinstance(owner, str)
        or not owner.strip()
    ):
        raise FinancialPolicyUnavailable("owner_unavailable")

    if not isinstance(limits, Mapping):
        raise FinancialPolicyUnavailable("limits_unavailable")

    high_water = await advance_persisted_high_water(
        session=session,
        owner=owner.strip(),
        currency=currency,
        verified_equity=verified_equity,
    )

    decision = evaluate_financial_policy(
        action=action,
        order_value=order_value,
        commission=commission,
        verified_equity=verified_equity,
        high_water_mark=high_water["new_peak"],
        limits=limits,
    )

    return {
        **decision,
        "owner_scoped": True,
        "high_water_revision": high_water["new_revision"],
        "high_water_peak": high_water["new_peak"],
        "high_water_update_pending":
            high_water["pending_transaction_commit"],
        "transaction_consistent": False,
        "execution_authorized": False,
        "commit_required": True,
    }
