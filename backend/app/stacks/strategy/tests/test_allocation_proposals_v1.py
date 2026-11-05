from __future__ import annotations

import pytest

from backend.app.stacks.strategy.allocation_proposals_v1 import (
    ALLOCATION_PROPOSAL_STRATEGY_NAMES,
    AllocationProposalUnavailableError,
    build_equal_weight_portfolio,
    build_permanent_portfolio,
    build_sixty_forty_rebalanced_portfolio,
)

UNIVERSE = (
    "SPY", "QQQ", "IWM", "DIA",
    "XLK", "XLF", "XLE", "XLV",
    "XLY", "XLP", "XLI", "XLU",
    "XLB", "XLRE", "TLT", "GLD",
)


def _bars() -> list[dict[str, float]]:
    return [
        {
            "close": 100.0 + index,
        }
        for index in range(253)
    ]


def _universe_bars() -> dict[str, list[dict[str, float]]]:
    return {
        symbol: _bars()
        for symbol in UNIVERSE
    }


def test_exact_three_identity():
    assert ALLOCATION_PROPOSAL_STRATEGY_NAMES == (
        "60/40 Rebalanced Portfolio",
        "Equal Weight Portfolio",
        "Permanent Portfolio",
    )


def test_equal_weight_proposal_is_non_executable_and_conserved():
    output = build_equal_weight_portfolio(
        universe_symbols=UNIVERSE,
        universe_bars=_universe_bars(),
    )

    assert len(output["target_weights"]) == 16
    assert sum(output["target_weights"].values()) == pytest.approx(1.0)
    assert output["cash_weight"] == 0.0
    assert output["execution_enabled"] is False


def test_sixty_forty_proposal_is_exact_and_non_executable():
    output = build_sixty_forty_rebalanced_portfolio(
        universe_symbols=UNIVERSE,
        universe_bars=_universe_bars(),
    )

    assert output["target_weights"] == {
        "SPY": 0.60,
        "TLT": 0.40,
    }
    assert output["execution_enabled"] is False


def test_permanent_portfolio_retains_cash_explicitly():
    output = build_permanent_portfolio(
        universe_symbols=UNIVERSE,
        universe_bars=_universe_bars(),
    )

    assert output["target_weights"] == {
        "GLD": 0.25,
        "SPY": 0.25,
        "TLT": 0.25,
    }
    assert output["cash_weight"] == 0.25
    assert output["broker_order_generation_enabled"] is False


@pytest.mark.parametrize(
    "builder",
    (
        build_sixty_forty_rebalanced_portfolio,
        build_permanent_portfolio,
    ),
)
def test_required_anchor_absence_fails_closed(builder):
    with pytest.raises(AllocationProposalUnavailableError):
        builder(
            universe_symbols=("SPY", "QQQ"),
            universe_bars={
                "SPY": _bars(),
                "QQQ": _bars(),
            },
        )


def test_insufficient_history_fails_closed():
    data = _universe_bars()
    data["XLK"] = data["XLK"][:252]

    with pytest.raises(AllocationProposalUnavailableError):
        build_equal_weight_portfolio(
            universe_symbols=UNIVERSE,
            universe_bars=data,
        )
