"""Deterministic, non-executable allocation proposal builders."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from math import isfinite
from typing import Any

from backend.app.stacks.strategy.allocation_proposal import (
    AllocationProposalError,
    build_allocation_proposal,
)

ALLOCATION_PROPOSAL_STRATEGY_NAMES = (
    "60/40 Rebalanced Portfolio",
    "Equal Weight Portfolio",
    "Permanent Portfolio",
)

_REQUIRED_HISTORY = 253


class AllocationProposalUnavailableError(ValueError):
    """Raised when truthful universe history cannot support a proposal."""


def _normalized_symbols(
    universe_symbols: Iterable[object],
) -> tuple[str, ...]:
    symbols = tuple(
        str(value).strip().upper()
        for value in universe_symbols
    )

    if len(symbols) < 2 or not all(symbols):
        raise AllocationProposalUnavailableError(
            "owner universe must contain at least two non-empty symbols"
        )

    if len(set(symbols)) != len(symbols):
        raise AllocationProposalUnavailableError(
            "owner universe symbols must be unique"
        )

    return symbols


def _validate_history(
    universe_bars: Mapping[object, object],
    required_symbols: Iterable[str],
) -> None:
    if not isinstance(universe_bars, Mapping):
        raise AllocationProposalUnavailableError(
            "universe historical bars must be a mapping"
        )

    for symbol in required_symbols:
        bars = universe_bars.get(symbol)

        if (
            isinstance(bars, (str, bytes))
            or not isinstance(bars, Sequence)
            or len(bars) < _REQUIRED_HISTORY
        ):
            raise AllocationProposalUnavailableError(
                f"insufficient truthful daily history for {symbol}"
            )

        for bar in bars[-_REQUIRED_HISTORY:]:
            try:
                close = float(bar["close"])
            except (KeyError, TypeError, ValueError) as exc:
                raise AllocationProposalUnavailableError(
                    f"invalid truthful daily history for {symbol}"
                ) from exc

            if not isfinite(close) or close <= 0.0:
                raise AllocationProposalUnavailableError(
                    f"invalid truthful daily history for {symbol}"
                )


def build_equal_weight_portfolio(
    *,
    universe_symbols: Iterable[object],
    universe_bars: Mapping[object, object],
) -> dict[str, object]:
    """Propose equal weights across every owner-universe symbol."""

    symbols = _normalized_symbols(universe_symbols)
    _validate_history(universe_bars, symbols)

    return build_allocation_proposal(
        strategy_name="Equal Weight Portfolio",
        universe_symbols=symbols,
        target_weights={
            symbol: 1.0 / len(symbols)
            for symbol in symbols
        },
    )


def build_sixty_forty_rebalanced_portfolio(
    *,
    universe_symbols: Iterable[object],
    universe_bars: Mapping[object, object],
) -> dict[str, object]:
    """Propose a fixed 60% SPY / 40% TLT allocation."""

    symbols = _normalized_symbols(universe_symbols)
    required = ("SPY", "TLT")

    if not set(required) <= set(symbols):
        raise AllocationProposalUnavailableError(
            "60/40 proposal requires SPY and TLT in the owner universe"
        )

    _validate_history(universe_bars, required)

    return build_allocation_proposal(
        strategy_name="60/40 Rebalanced Portfolio",
        universe_symbols=symbols,
        target_weights={
            "SPY": 0.60,
            "TLT": 0.40,
        },
    )


def build_permanent_portfolio(
    *,
    universe_symbols: Iterable[object],
    universe_bars: Mapping[object, object],
) -> dict[str, object]:
    """Propose 25% each SPY, TLT, GLD, and cash."""

    symbols = _normalized_symbols(universe_symbols)
    required = ("SPY", "TLT", "GLD")

    if not set(required) <= set(symbols):
        raise AllocationProposalUnavailableError(
            "Permanent Portfolio requires SPY, TLT, and GLD"
        )

    _validate_history(universe_bars, required)

    return build_allocation_proposal(
        strategy_name="Permanent Portfolio",
        universe_symbols=symbols,
        target_weights={
            "SPY": 0.25,
            "TLT": 0.25,
            "GLD": 0.25,
        },
        cash_weight=0.25,
    )


def healthcheck() -> dict[str, object]:
    return {
        "status": "ok",
        "strategy_names": ALLOCATION_PROPOSAL_STRATEGY_NAMES,
        "strategy_count": 3,
        "registry_activated": False,
        "provider_called": False,
        "database_accessed": False,
        "broker_order_generation_enabled": False,
        "execution_enabled": False,
    }
