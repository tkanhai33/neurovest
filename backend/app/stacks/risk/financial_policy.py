from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Mapping


class FinancialPolicyUnavailable(ValueError):
    """A financial risk decision could not be verified."""


def _amount(value: object, name: str) -> Decimal:
    if value is None or isinstance(value, bool):
        raise FinancialPolicyUnavailable(f"{name}_unavailable")

    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError, OverflowError):
        raise FinancialPolicyUnavailable(f"{name}_invalid") from None

    if not number.is_finite() or number < 0:
        raise FinancialPolicyUnavailable(f"{name}_invalid")

    return number


def _positive(value: object, name: str) -> Decimal:
    number = _amount(value, name)

    if number <= 0:
        raise FinancialPolicyUnavailable(f"{name}_invalid")

    return number


def evaluate_financial_policy(
    *,
    action: str,
    order_value: object,
    commission: object,
    verified_equity: Mapping[str, object],
    high_water_mark: object,
    limits: Mapping[str, object],
) -> dict:
    """
    Pure paper-trading financial policy calculation.

    Requires a complete, genuinely verified equity snapshot.
    Does not fetch market data, authorize trading, acquire
    database locks, or persist a high-water mark.

    This result is NOT final execution authorization.
    The entire evaluation must eventually be repeated using
    authoritative state inside the serialized ledger boundary.
    """
    if not isinstance(action, str):
        raise FinancialPolicyUnavailable("action_invalid")

    side = action.strip().lower()
    if side not in {"buy", "sell"}:
        raise FinancialPolicyUnavailable("action_invalid")

    if not isinstance(verified_equity, Mapping):
        raise FinancialPolicyUnavailable("equity_unavailable")

    if verified_equity.get("status") != "verified":
        raise FinancialPolicyUnavailable("equity_not_verified")

    if verified_equity.get("risk_limits_enforced") is not False:
        raise FinancialPolicyUnavailable("equity_contract_invalid")

    if not isinstance(limits, Mapping):
        raise FinancialPolicyUnavailable("limits_unavailable")

    cash = _amount(verified_equity.get("cash"), "cash")
    equity = _positive(
        verified_equity.get("net_liquidation_value"),
        "net_liquidation_value",
    )
    exposure = _amount(
        verified_equity.get("gross_long_exposure"),
        "gross_long_exposure",
    )
    # Long-only valuation invariant: never trust a claimed
    # equity value that cannot be reconciled to marked assets.
    if cash + exposure != equity:
        raise FinancialPolicyUnavailable(
            "portfolio_equity_reconciliation_failed"
        )

    value = _positive(order_value, "order_value")
    fee = _amount(commission, "commission")

    peak = _positive(high_water_mark, "high_water_mark")

    max_order = _positive(
        limits.get("max_order_value"),
        "max_order_value",
    )
    max_exposure = _positive(
        limits.get("max_gross_exposure"),
        "max_gross_exposure",
    )
    max_drawdown = _amount(
        limits.get("max_drawdown_fraction"),
        "max_drawdown_fraction",
    )

    if max_drawdown >= 1:
        raise FinancialPolicyUnavailable(
            "max_drawdown_fraction_invalid"
        )

    if equity > peak:
        raise FinancialPolicyUnavailable(
            "high_water_mark_outdated"
        )

    # Long-only paper portfolios. Short-selling is unsupported.
    if side == "sell" and value > exposure:
        return {
            "approved": False,
            "reason": "insufficient_marked_exposure",
        }

    projected_exposure = (
        exposure + value
        if side == "buy"
        else exposure - value
    )

    drawdown = (peak - equity) / peak

    if drawdown > max_drawdown:
        reason = "max_equity_drawdown_exceeded"
    elif value > max_order:
        reason = "max_order_value_exceeded"
    elif side == "buy" and value + fee > cash:
        reason = "insufficient_cash"
    elif projected_exposure > max_exposure:
        # Even a sell cannot claim compliance if exposure
        # remains above the configured aggregate limit.
        reason = "max_gross_exposure_exceeded"
    else:
        reason = "financial_policy_ok"

    return {
        "approved": reason == "financial_policy_ok",
        "reason": reason,
        "action": side,
        "order_value": str(value),
        "current_cash": str(cash),
        "current_equity": str(equity),
        "current_exposure": str(exposure),
        "projected_gross_exposure": str(projected_exposure),
        "drawdown_fraction": str(drawdown),
        "max_drawdown_fraction": str(max_drawdown),
        "max_order_value": str(max_order),
        "max_gross_exposure": str(max_exposure),
        "execution_authorized": False,
        "transaction_consistent": False,
    }
