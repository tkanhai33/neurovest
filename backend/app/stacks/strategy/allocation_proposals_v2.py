"""Deterministic, non-executable dynamic allocation proposals."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from math import isfinite, sqrt

from backend.app.stacks.strategy.allocation_proposal import (
    build_allocation_proposal,
)
from backend.app.stacks.strategy.allocation_proposals_v1 import (
    AllocationProposalUnavailableError,
    _normalized_symbols,
    _validate_history,
)

ALLOCATION_PROPOSAL_STRATEGY_NAMES_V2 = (
    "Inverse Volatility Weighting",
    "Momentum Weighted Portfolio",
    "Trend-Following Asset Allocation",
)

_RETURN_WINDOW = 63
_MOMENTUM_WINDOW = 126
_TREND_WINDOW = 200
_TREND_ANCHORS = ("SPY", "TLT", "GLD")


def _closes(
    bars: Sequence[object],
) -> list[float]:
    return [
        float(bar["close"])
        for bar in bars
    ]


def _returns(
    closes: list[float],
    window: int,
) -> list[float]:
    return [
        closes[index] / closes[index - 1] - 1.0
        for index in range(
            len(closes) - window,
            len(closes),
        )
    ]


def _sample_volatility(
    values: list[float],
) -> float:
    if len(values) < 2:
        raise AllocationProposalUnavailableError(
            "insufficient daily returns for volatility"
        )

    average = sum(values) / len(values)

    variance = sum(
        (value - average) ** 2
        for value in values
    ) / (len(values) - 1)

    volatility = sqrt(variance)

    if not isfinite(volatility) or volatility <= 0.0:
        raise AllocationProposalUnavailableError(
            "non-positive realized volatility"
        )

    return volatility


def build_inverse_volatility_weighting(
    *,
    universe_symbols: Iterable[object],
    universe_bars: Mapping[object, object],
) -> dict[str, object]:
    """Weight every universe member inversely to 63-day volatility."""

    symbols = _normalized_symbols(universe_symbols)
    _validate_history(universe_bars, symbols)

    inverse_volatility = {
        symbol: 1.0 / _sample_volatility(
            _returns(
                _closes(universe_bars[symbol]),
                _RETURN_WINDOW,
            )
        )
        for symbol in symbols
    }

    denominator = sum(inverse_volatility.values())

    if not isfinite(denominator) or denominator <= 0.0:
        raise AllocationProposalUnavailableError(
            "invalid inverse-volatility denominator"
        )

    return build_allocation_proposal(
        strategy_name="Inverse Volatility Weighting",
        universe_symbols=symbols,
        target_weights={
            symbol: value / denominator
            for symbol, value in inverse_volatility.items()
        },
    )


def build_momentum_weighted_portfolio(
    *,
    universe_symbols: Iterable[object],
    universe_bars: Mapping[object, object],
) -> dict[str, object]:
    """Weight every universe member by relative 126-day momentum."""

    symbols = _normalized_symbols(universe_symbols)
    _validate_history(universe_bars, symbols)

    momentum = {
        symbol: (
            _closes(universe_bars[symbol])[-1]
            / _closes(universe_bars[symbol])[-1 - _MOMENTUM_WINDOW]
            - 1.0
        )
        for symbol in symbols
    }

    floor = min(momentum.values())
    relative_scores = {
        symbol: score - floor + 1e-6
        for symbol, score in momentum.items()
    }
    denominator = sum(relative_scores.values())

    if not isfinite(denominator) or denominator <= 0.0:
        raise AllocationProposalUnavailableError(
            "invalid relative-momentum denominator"
        )

    return build_allocation_proposal(
        strategy_name="Momentum Weighted Portfolio",
        universe_symbols=symbols,
        target_weights={
            symbol: value / denominator
            for symbol, value in relative_scores.items()
        },
    )


def build_trend_following_asset_allocation(
    *,
    universe_symbols: Iterable[object],
    universe_bars: Mapping[object, object],
) -> dict[str, object]:
    """Allocate equally to trend-positive SPY, TLT, and GLD; retain cash otherwise."""

    symbols = _normalized_symbols(universe_symbols)

    if not set(_TREND_ANCHORS) <= set(symbols):
        raise AllocationProposalUnavailableError(
            "trend allocation requires SPY, TLT, and GLD"
        )

    _validate_history(universe_bars, _TREND_ANCHORS)

    selected = [
        symbol
        for symbol in _TREND_ANCHORS
        if _closes(universe_bars[symbol])[-1]
        > sum(
            _closes(universe_bars[symbol])[-_TREND_WINDOW:]
        ) / _TREND_WINDOW
    ]

    target_weight = 1.0 / len(_TREND_ANCHORS)

    return build_allocation_proposal(
        strategy_name="Trend-Following Asset Allocation",
        universe_symbols=symbols,
        target_weights={
            symbol: target_weight
            for symbol in selected
        },
        cash_weight=1.0 - target_weight * len(selected),
    )
