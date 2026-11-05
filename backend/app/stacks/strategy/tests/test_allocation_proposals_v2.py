from __future__ import annotations

import pytest

from backend.app.stacks.strategy.allocation_proposals_v2 import (
    ALLOCATION_PROPOSAL_STRATEGY_NAMES_V2,
    build_inverse_volatility_weighting,
    build_momentum_weighted_portfolio,
    build_trend_following_asset_allocation,
)

UNIVERSE = (
    "SPY", "QQQ", "IWM", "DIA",
    "XLK", "XLF", "XLE", "XLV",
    "XLY", "XLP", "XLI", "XLU",
    "XLB", "XLRE", "TLT", "GLD",
)


def _bars(
    daily_return: float,
) -> list[dict[str, float]]:
    close = 100.0
    output = []

    for index in range(253):
        output.append({"close": close})
        close *= 1.0 + daily_return * (
            1.0 if index % 2 else 0.35
        )

    return output


def _universe_bars() -> dict[str, list[dict[str, float]]]:
    data = {
        symbol: _bars(0.0005)
        for symbol in UNIVERSE
    }

    data["XLK"] = _bars(0.0020)
    data["SPY"] = _bars(0.0015)
    data["TLT"] = _bars(0.0010)
    data["GLD"] = _bars(-0.0010)

    return data


def _total(
    proposal: dict[str, object],
) -> float:
    return (
        sum(proposal["target_weights"].values())
        + proposal["cash_weight"]
    )


def test_exact_three_identity():
    assert ALLOCATION_PROPOSAL_STRATEGY_NAMES_V2 == (
        "Inverse Volatility Weighting",
        "Momentum Weighted Portfolio",
        "Trend-Following Asset Allocation",
    )


def test_inverse_volatility_proposal_is_conserved_and_non_executable():
    proposal = build_inverse_volatility_weighting(
        universe_symbols=UNIVERSE,
        universe_bars=_universe_bars(),
    )

    assert len(proposal["target_weights"]) == 16
    assert _total(proposal) == pytest.approx(1.0)
    assert proposal["execution_enabled"] is False


def test_momentum_weighting_favors_strongest_relative_momentum():
    proposal = build_momentum_weighted_portfolio(
        universe_symbols=UNIVERSE,
        universe_bars=_universe_bars(),
    )

    assert proposal["target_weights"]["XLK"] == max(
        proposal["target_weights"].values()
    )
    assert _total(proposal) == pytest.approx(1.0)
    assert proposal["execution_enabled"] is False


def test_trend_allocation_uses_cash_for_non_confirming_anchors():
    proposal = build_trend_following_asset_allocation(
        universe_symbols=UNIVERSE,
        universe_bars=_universe_bars(),
    )

    assert proposal["target_weights"] == {
        "SPY": pytest.approx(1.0 / 3.0),
        "TLT": pytest.approx(1.0 / 3.0),
    }
    assert proposal["cash_weight"] == pytest.approx(1.0 / 3.0)
    assert _total(proposal) == pytest.approx(1.0)
    assert proposal["execution_enabled"] is False
