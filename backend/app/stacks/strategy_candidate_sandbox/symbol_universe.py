"""
130G_SYMBOL_UNIVERSE_LOCK

Replay-only symbol universe classification.

Does NOT block symbols globally.
Provides recommendations for replay/training.
"""

from __future__ import annotations

TRAIN_MORE = {
    "CNR.TO",
}

WATCHLIST = {
    "ENB.TO",
    "VFV.TO",
    "VUN.TO",
}

WEAK = {
    "BAM.TO",
    "RY.TO",
    "TD.TO",
}

EXCLUDED = {
    "SHOP.TO",
    "ATZ.TO",
    "BNS.TO",
}


def classify_symbol(symbol: str) -> str:

    symbol = symbol.upper()

    if symbol in TRAIN_MORE:
        return "TRAIN_MORE"

    if symbol in WATCHLIST:
        return "WATCHLIST"

    if symbol in WEAK:
        return "WEAK"

    if symbol in EXCLUDED:
        return "EXCLUDED"

    return "UNKNOWN"


def replay_allowed(symbol: str) -> bool:

    return classify_symbol(symbol) != "EXCLUDED"


def preferred_training_symbols():

    return sorted(TRAIN_MORE | WATCHLIST)


def excluded_symbols():

    return sorted(EXCLUDED)


def universe_summary():

    return {

        "train_more": sorted(TRAIN_MORE),

        "watchlist": sorted(WATCHLIST),

        "weak": sorted(WEAK),

        "excluded": sorted(EXCLUDED),

    }
