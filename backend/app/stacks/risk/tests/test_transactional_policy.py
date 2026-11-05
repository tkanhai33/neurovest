from __future__ import annotations

from copy import deepcopy
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

import backend.app.stacks.risk.transactional_policy as coordinator
from backend.app.stacks.risk.financial_policy import (
    FinancialPolicyUnavailable,
)


LIMITS = {
    "max_order_value": "1000",
    "max_gross_exposure": "5000",
    "max_drawdown_fraction": "0.20",
}

EQUITY = {
    "status": "verified",
    "cash": "8000",
    "gross_long_exposure": "2000",
    "net_liquidation_value": "10000",
    "risk_limits_enforced": False,
}


@pytest.fixture
def locked_peak(monkeypatch):
    mocked = AsyncMock(return_value={
        "new_peak": "10000",
        "new_revision": 3,
        "pending_transaction_commit": False,
    })
    monkeypatch.setattr(
        coordinator,
        "advance_persisted_high_water",
        mocked,
    )
    return mocked


async def evaluate(
    *,
    owner="owner-1",
    action="buy",
    value="500",
    equity=None,
    limits=None,
):
    return await coordinator.evaluate_transactional_financial_policy(
        session=object(),
        owner=owner,
        currency="USD",
        action=action,
        order_value=value,
        commission="1",
        verified_equity=deepcopy(EQUITY)
            if equity is None else equity,
        limits=deepcopy(LIMITS)
            if limits is None else limits,
    )


async def test_valid_decision_is_not_execution_authorization(
    locked_peak,
):
    result = await evaluate()

    assert result["approved"] is True
    assert result["execution_authorized"] is False
    assert result["transaction_consistent"] is False
    assert result["commit_required"] is True
    assert result["high_water_revision"] == 3

    locked_peak.assert_awaited_once()


async def test_owner_propagated_to_state_lock(locked_peak):
    await evaluate(owner=" owner-1 ")

    kwargs = locked_peak.await_args.kwargs
    assert kwargs["owner"] == "owner-1"
    assert kwargs["currency"] == "USD"


async def test_overexposure_rejected(locked_peak):
    equity = {
        **EQUITY,
        "cash": "4000",
        "gross_long_exposure": "6000",
    }
    result = await evaluate(equity=equity)

    assert result["approved"] is False
    assert result["reason"] == "max_gross_exposure_exceeded"


async def test_invalid_equity_never_locks_state(locked_peak):
    with pytest.raises(FinancialPolicyUnavailable):
        await evaluate(equity={
            **EQUITY,
            "status": "unavailable",
        })

    locked_peak.assert_not_awaited()


async def test_blank_owner_never_locks_state(locked_peak):
    with pytest.raises(FinancialPolicyUnavailable):
        await evaluate(owner=" ")

    locked_peak.assert_not_awaited()


async def test_lock_failure_blocks_policy(locked_peak):
    locked_peak.side_effect = RuntimeError("DB unavailable")

    with pytest.raises(RuntimeError):
        await evaluate()


async def test_new_peak_is_used_by_drawdown(locked_peak):
    locked_peak.return_value = {
        "new_peak": "12000",
        "new_revision": 4,
        "pending_transaction_commit": True,
    }

    result = await evaluate()

    assert Decimal(result["drawdown_fraction"]) == (
        Decimal("12000") - Decimal("10000")
    ) / Decimal("12000")
    assert result["high_water_update_pending"] is True
    assert result["execution_authorized"] is False


async def test_invalid_policy_blocks(locked_peak):
    with pytest.raises(FinancialPolicyUnavailable):
        await evaluate(limits={})


async def test_invalid_action_blocks(locked_peak):
    with pytest.raises(FinancialPolicyUnavailable):
        await coordinator.evaluate_transactional_financial_policy(
            session=object(),
            owner="owner-1",
            currency="USD",
            action="short",
            order_value="500",
            commission="1",
            verified_equity=EQUITY,
            limits=LIMITS,
        )
