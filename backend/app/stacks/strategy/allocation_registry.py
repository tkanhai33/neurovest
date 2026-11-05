"""Explicit registry for proposal-only allocation strategies."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping

from backend.app.stacks.strategy.allocation_proposals_v1 import (
    build_equal_weight_portfolio,
    build_permanent_portfolio,
    build_sixty_forty_rebalanced_portfolio,
)
from backend.app.stacks.strategy.allocation_proposals_v2 import (
    build_inverse_volatility_weighting,
    build_momentum_weighted_portfolio,
    build_trend_following_asset_allocation,
)

AllocationBuilder = Callable[
    ...,
    dict[str, object],
]

ALLOCATION_PROPOSAL_EVALUATOR_ORDER = (
    "Equal Weight Portfolio",
    "60/40 Rebalanced Portfolio",
    "Permanent Portfolio",
    "Inverse Volatility Weighting",
    "Momentum Weighted Portfolio",
    "Trend-Following Asset Allocation",
)

ALLOCATION_PROPOSAL_EVALUATORS = {
    "Equal Weight Portfolio": build_equal_weight_portfolio,
    "60/40 Rebalanced Portfolio": build_sixty_forty_rebalanced_portfolio,
    "Permanent Portfolio": build_permanent_portfolio,
    "Inverse Volatility Weighting": build_inverse_volatility_weighting,
    "Momentum Weighted Portfolio": build_momentum_weighted_portfolio,
    "Trend-Following Asset Allocation": (
        build_trend_following_asset_allocation
    ),
}


def selected_allocation_proposal_names(
    enabled_names: Iterable[object],
) -> tuple[str, ...]:
    enabled = {
        str(name).strip()
        for name in enabled_names
        if str(name).strip()
    }

    return tuple(
        name
        for name in ALLOCATION_PROPOSAL_EVALUATOR_ORDER
        if name in enabled
    )


def healthcheck() -> dict[str, object]:
    return {
        "status": "ok",
        "strategy_names": ALLOCATION_PROPOSAL_EVALUATOR_ORDER,
        "strategy_count": len(ALLOCATION_PROPOSAL_EVALUATORS),
        "decision_registry_modified": False,
        "activation_required": True,
        "broker_order_generation_enabled": False,
        "execution_enabled": False,
    }
