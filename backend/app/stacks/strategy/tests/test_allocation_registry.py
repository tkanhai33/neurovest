from backend.app.stacks.strategy.allocation_registry import (
    ALLOCATION_PROPOSAL_EVALUATOR_ORDER,
    ALLOCATION_PROPOSAL_EVALUATORS,
    selected_allocation_proposal_names,
)


def test_exact_three_proposal_only_strategy_identities():
    assert tuple(ALLOCATION_PROPOSAL_EVALUATORS) == (
        "Equal Weight Portfolio",
        "60/40 Rebalanced Portfolio",
        "Permanent Portfolio",
        "Inverse Volatility Weighting",
        "Momentum Weighted Portfolio",
        "Trend-Following Asset Allocation",
    )
    assert ALLOCATION_PROPOSAL_EVALUATOR_ORDER == tuple(
        ALLOCATION_PROPOSAL_EVALUATORS
    )


def test_selection_is_allowlisted_and_deterministic():
    assert selected_allocation_proposal_names(
        [
            "Permanent Portfolio",
            "unknown strategy",
            "Equal Weight Portfolio",
        ]
    ) == (
        "Equal Weight Portfolio",
        "Permanent Portfolio",
    )
