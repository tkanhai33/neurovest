from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Mapping


class HighWaterStateUnavailable(ValueError):
    """Cannot establish trustworthy persistent drawdown state."""


def _positive(value: object, field: str) -> Decimal:
    if value is None or isinstance(value, bool):
        raise HighWaterStateUnavailable(field + "_unavailable")
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError, OverflowError):
        raise HighWaterStateUnavailable(field + "_invalid") from None
    if not number.is_finite() or number <= 0:
        raise HighWaterStateUnavailable(field + "_invalid")
    return number


def advance_high_water(
    *,
    owner: str,
    verified_equity: Mapping[str, object],
    stored_peak: object,
    stored_revision: object,
) -> dict:
    """
    Deterministic state transition for an EXISTING owner record.

    Persistence must occur under the same owner transaction lock
    as order authorization. Never infer a missing initial peak
    from a cash balance, largest order, or starting capital.

    Does not write to the DB or authorize execution.
    """
    if not isinstance(owner, str) or not owner.strip():
        raise HighWaterStateUnavailable("owner_unavailable")

    if not isinstance(verified_equity, Mapping):
        raise HighWaterStateUnavailable("equity_unavailable")

    if verified_equity.get("status") != "verified":
        raise HighWaterStateUnavailable("equity_unverified")

    if verified_equity.get("risk_limits_enforced") is not False:
        raise HighWaterStateUnavailable("equity_contract_invalid")

    cash = _positive_or_zero(verified_equity.get("cash"), "cash")
    exposure = _positive_or_zero(
        verified_equity.get("gross_long_exposure"),
        "gross_long_exposure",
    )
    equity = _positive(
        verified_equity.get("net_liquidation_value"),
        "net_liquidation_value",
    )

    if cash + exposure != equity:
        raise HighWaterStateUnavailable("equity_reconciliation_failed")

    peak = _positive(stored_peak, "stored_peak")

    if (
        isinstance(stored_revision, bool)
        or not isinstance(stored_revision, int)
        or stored_revision < 1
    ):
        raise HighWaterStateUnavailable("stored_revision_invalid")

    new_peak = max(peak, equity)
    return {
        "owner": owner.strip(),
        "previous_peak": str(peak),
        "new_peak": str(new_peak),
        "equity": str(equity),
        "drawdown_fraction": str((new_peak - equity) / new_peak),
        "previous_revision": stored_revision,
        "new_revision": (
            stored_revision + 1 if new_peak > peak
            else stored_revision
        ),
        "peak_changed": new_peak > peak,
        "execution_authorized": False,
        "persisted": False,
    }


def _positive_or_zero(value: object, field: str) -> Decimal:
    if value is None or isinstance(value, bool):
        raise HighWaterStateUnavailable(field + "_unavailable")
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError, OverflowError):
        raise HighWaterStateUnavailable(field + "_invalid") from None
    if not number.is_finite() or number < 0:
        raise HighWaterStateUnavailable(field + "_invalid")
    return number
