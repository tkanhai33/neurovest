from __future__ import annotations

from copy import deepcopy

import pytest

from backend.app.stacks.risk.financial_policy import (
    FinancialPolicyUnavailable,
    evaluate_financial_policy,
)


LIMITS = {
    "max_order_value": "1000",
    "max_gross_exposure": "5000",
    "max_drawdown_fraction": "0.20",
}

EQUITY = {
    "status": "verified",
    "cash": "4000",
    "net_liquidation_value": "10000",
    "gross_long_exposure": "6000",
    "risk_limits_enforced": False,
}


def evaluate(
    *,
    action="buy",
    order_value="500",
    commission="1",
    equity=None,
    peak="10000",
    limits=None,
):
    return evaluate_financial_policy(
        action=action,
        order_value=order_value,
        commission=commission,
        verified_equity=(
            deepcopy(EQUITY) if equity is None else equity
        ),
        high_water_mark=peak,
        limits=deepcopy(LIMITS) if limits is None else limits,
    )


def test_buy_rejected_when_exposure_exceeds_limit():
    result = evaluate()
    assert result["approved"] is False
    assert result["reason"] == "max_gross_exposure_exceeded"
    assert result["execution_authorized"] is False


def test_sell_can_reduce_exposure_below_limit():
    result = evaluate(action="sell", order_value="1500")
    assert result["approved"] is False
    assert result["reason"] == "max_order_value_exceeded"


def test_allowed_buy_within_all_limits():
    equity = deepcopy(EQUITY)
    equity["gross_long_exposure"] = "2000"
    equity["cash"] = "8000"

    result = evaluate(equity=equity)

    assert result["approved"] is True
    assert result["reason"] == "financial_policy_ok"
    assert result["execution_authorized"] is False
    assert result["transaction_consistent"] is False


def test_allowed_sell_reduces_exposure():
    equity = deepcopy(EQUITY)
    equity["gross_long_exposure"] = "2000"
    equity["cash"] = "8000"

    result = evaluate(
        action="sell",
        order_value="500",
        equity=equity,
    )

    assert result["approved"] is True
    assert result["projected_gross_exposure"] == "1500"


def test_buying_power_includes_commission():
    equity = deepcopy(EQUITY)
    equity["cash"] = "500"
    equity["gross_long_exposure"] = "1000"
    equity["net_liquidation_value"] = "1500"

    result = evaluate(equity=equity, peak="1500")

    assert result["reason"] == "insufficient_cash"


def test_order_limit_rejection():
    equity = deepcopy(EQUITY)
    equity["gross_long_exposure"] = "1000"
    equity["cash"] = "9000"

    result = evaluate(
        equity=equity,
        order_value="1001",
    )

    assert result["reason"] == "max_order_value_exceeded"


def test_drawdown_rejection():
    equity = deepcopy(EQUITY)
    equity["gross_long_exposure"] = "1000"
    equity["cash"] = "6900"
    equity["net_liquidation_value"] = "7900"

    result = evaluate(equity=equity)

    assert result["reason"] == "max_equity_drawdown_exceeded"


def test_exact_drawdown_boundary():
    equity = deepcopy(EQUITY)
    equity["gross_long_exposure"] = "1000"
    equity["cash"] = "7000"
    equity["net_liquidation_value"] = "8000"

    result = evaluate(equity=equity)

    assert result["approved"] is True
    assert result["drawdown_fraction"] == "0.2"


def test_sell_cannot_exceed_total_exposure():
    result = evaluate(
        action="sell",
        order_value="7000",
    )
    assert result["reason"] == "insufficient_marked_exposure"


@pytest.mark.parametrize(
    "invalid",
    [None, "-1", "NaN", "Infinity", True, "bad"],
)
def test_invalid_order_values_fail_closed(invalid):
    with pytest.raises(FinancialPolicyUnavailable):
        evaluate(order_value=invalid)


@pytest.mark.parametrize(
    "invalid",
    [None, "-1", "NaN", "Infinity", True],
)
def test_invalid_cash_fails_closed(invalid):
    equity = deepcopy(EQUITY)
    equity["cash"] = invalid

    with pytest.raises(FinancialPolicyUnavailable):
        evaluate(equity=equity)


def test_unverified_equity_rejected():
    equity = deepcopy(EQUITY)
    equity["status"] = "unavailable"

    with pytest.raises(
        FinancialPolicyUnavailable,
        match="equity_not_verified",
    ):
        evaluate(equity=equity)


def test_missing_peak_fails_closed():
    with pytest.raises(FinancialPolicyUnavailable):
        evaluate(peak=None)


def test_outdated_peak_fails_closed():
    with pytest.raises(
        FinancialPolicyUnavailable,
        match="high_water_mark_outdated",
    ):
        evaluate(peak="9000")


def test_missing_limits_fail_closed():
    with pytest.raises(FinancialPolicyUnavailable):
        evaluate(limits={})


def test_invalid_drawdown_policy_rejected():
    values = deepcopy(LIMITS)
    values["max_drawdown_fraction"] = "1.5"

    with pytest.raises(FinancialPolicyUnavailable):
        evaluate(limits=values)


def test_short_selling_not_accepted():
    with pytest.raises(FinancialPolicyUnavailable):
        evaluate(action="short")


def test_no_authorization_from_isolated_decision():
    equity = deepcopy(EQUITY)
    equity["gross_long_exposure"] = "1000"
    equity["cash"] = "9000"

    result = evaluate(equity=equity)

    assert result["approved"] is True
    assert result["execution_authorized"] is False
    assert result["transaction_consistent"] is False


def test_inconsistent_equity_fails_closed():
    equity = deepcopy(EQUITY)
    equity["net_liquidation_value"] = "15000"

    with pytest.raises(
        FinancialPolicyUnavailable,
        match="portfolio_equity_reconciliation_failed",
    ):
        evaluate(equity=equity)


def test_unreconciled_exposure_fails_closed():
    equity = deepcopy(EQUITY)
    equity["gross_long_exposure"] = "1000"

    with pytest.raises(
        FinancialPolicyUnavailable,
        match="portfolio_equity_reconciliation_failed",
    ):
        evaluate(equity=equity)


def test_reconciled_multi_asset_value():
    equity = deepcopy(EQUITY)
    equity["cash"] = "2500"
    equity["gross_long_exposure"] = "7500"

    result = evaluate(
        action="sell",
        order_value="500",
        equity=equity,
    )

    assert result["approved"] is False
    assert result["reason"] == "max_gross_exposure_exceeded"
