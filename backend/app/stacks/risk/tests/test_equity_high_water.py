from __future__ import annotations

from copy import deepcopy

import pytest

from backend.app.stacks.risk.equity_high_water import (
    HighWaterStateUnavailable,
    advance_high_water,
)


EQUITY = {
    "status": "verified",
    "cash": "4000",
    "gross_long_exposure": "6000",
    "net_liquidation_value": "10000",
    "risk_limits_enforced": False,
}


def evaluate(*, peak="10000", revision=1, equity=None, owner="user-1"):
    return advance_high_water(
        owner=owner,
        verified_equity=deepcopy(EQUITY) if equity is None else equity,
        stored_peak=peak,
        stored_revision=revision,
    )


def test_same_equity_preserves_peak():
    value = evaluate()
    assert value["new_peak"] == "10000"
    assert value["new_revision"] == 1
    assert value["drawdown_fraction"] == "0"
    assert value["persisted"] is False


def test_new_equity_high_advances_peak():
    value = evaluate(peak="9000")
    assert value["new_peak"] == "10000"
    assert value["new_revision"] == 2
    assert value["peak_changed"] is True


def test_drawdown_does_not_lower_peak():
    state = deepcopy(EQUITY)
    state.update({
        "cash": "3000",
        "gross_long_exposure": "5000",
        "net_liquidation_value": "8000",
    })
    value = evaluate(equity=state)
    assert value["new_peak"] == "10000"
    assert value["drawdown_fraction"] == "0.2"
    assert value["new_revision"] == 1


@pytest.mark.parametrize(
    "peak",
    [None, "0", "-1", "NaN", "Infinity", True],
)
def test_missing_or_invalid_stored_peak_rejected(peak):
    with pytest.raises(HighWaterStateUnavailable):
        evaluate(peak=peak)


@pytest.mark.parametrize("revision", [None, 0, -1, "1", True])
def test_invalid_revision_rejected(revision):
    with pytest.raises(HighWaterStateUnavailable):
        evaluate(revision=revision)


def test_missing_owner_rejected():
    with pytest.raises(HighWaterStateUnavailable):
        evaluate(owner=" ")


def test_unverified_equity_rejected():
    state = deepcopy(EQUITY)
    state["status"] = "unavailable"
    with pytest.raises(HighWaterStateUnavailable):
        evaluate(equity=state)


def test_inconsistent_equity_rejected():
    state = deepcopy(EQUITY)
    state["net_liquidation_value"] = "15000"
    with pytest.raises(
        HighWaterStateUnavailable,
        match="equity_reconciliation_failed",
    ):
        evaluate(equity=state)


def test_no_execution_permission_granted():
    value = evaluate()
    assert value["execution_authorized"] is False
    assert value["persisted"] is False
