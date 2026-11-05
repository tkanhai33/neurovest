import pytest

from backend.app.stacks.strategy.allocation_proposal import (
    AllocationProposalError,
    build_allocation_proposal,
)


def test_builds_canonical_proposal_only_envelope():
    output = build_allocation_proposal(
        strategy_name="Equal Weight Portfolio",
        universe_symbols=("SPY", "TLT", "GLD"),
        target_weights={"GLD": 0.25, "SPY": 0.50},
        cash_weight=0.25,
    )

    assert output["target_weights"] == {"GLD": 0.25, "SPY": 0.5}
    assert output["cash_weight"] == 0.25
    assert output["rebalance_action"] == "proposal_only"
    assert output["broker_order_generation_enabled"] is False
    assert output["execution_enabled"] is False


@pytest.mark.parametrize(
    "weights,cash",
    (
        ({"SPY": 0.8}, 0.1),
        ({"AAPL": 0.5}, 0.5),
        ({"SPY": -0.1}, 1.1),
    ),
)
def test_rejects_invalid_or_nonconserving_allocations(weights, cash):
    with pytest.raises(AllocationProposalError):
        build_allocation_proposal(
            strategy_name="Test",
            universe_symbols=("SPY", "TLT"),
            target_weights=weights,
            cash_weight=cash,
        )



def test_allows_cash_only_proposal_when_fully_unallocated():
    output = build_allocation_proposal(
        strategy_name="Trend-Following Asset Allocation",
        universe_symbols=("SPY", "TLT", "GLD"),
        target_weights={},
        cash_weight=1.0,
    )

    assert output["target_weights"] == {}
    assert output["cash_weight"] == 1.0
    assert output["execution_enabled"] is False
