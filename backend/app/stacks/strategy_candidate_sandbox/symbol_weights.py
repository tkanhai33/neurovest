"""
130I_UNIVERSE_WEIGHTING_PLAN

Replay/training symbol weights.

Does not execute trades.
Does not touch broker.
Does not change live portfolio.
"""

from __future__ import annotations

SYMBOL_WEIGHTS = {
    "CNR.TO": 4.0,
    "ENB.TO": 1.5,
    "VUN.TO": 1.0,
    "VFV.TO": 1.0,
}

def get_symbol_weight(symbol: str) -> float:
    return float(SYMBOL_WEIGHTS.get(symbol.upper(), 0.0))

def weighted_symbols() -> dict[str, float]:
    return dict(SYMBOL_WEIGHTS)

def preferred_weighted_order() -> list[str]:
    return [
        symbol
        for symbol, _weight in sorted(
            SYMBOL_WEIGHTS.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    ]
