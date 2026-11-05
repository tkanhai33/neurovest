from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import json


MARKET_CRYPTO = "crypto"
MARKET_EQUITIES = "equities"
MARKET_FOREX = "forex"
MARKET_FUTURES = "futures"
MARKET_OPTIONS = "options"
MARKET_FIXED_INCOME = "fixed_income"
MARKET_COMMODITIES = "commodities"
MARKET_MULTI_ASSET = "multi_asset"

# Legacy constant preserved only for import compatibility.
#
# It is metadata vocabulary only and is no longer a specific-market
# wildcard.
MARKET_CROSS = "cross_market"


SUPPORTED_MARKETS = (
    MARKET_CRYPTO,
    MARKET_EQUITIES,
    MARKET_FOREX,
    MARKET_FUTURES,
    MARKET_OPTIONS,
    MARKET_FIXED_INCOME,
    MARKET_COMMODITIES,
    MARKET_MULTI_ASSET,
)


MARKET_ALIASES = {
    "crypto":
        MARKET_CRYPTO,

    "cryptocurrency":
        MARKET_CRYPTO,

    "cryptocurrencies":
        MARKET_CRYPTO,

    "equity":
        MARKET_EQUITIES,

    "equities":
        MARKET_EQUITIES,

    "stock":
        MARKET_EQUITIES,

    "stocks":
        MARKET_EQUITIES,

    "forex":
        MARKET_FOREX,

    "fx":
        MARKET_FOREX,

    "foreign_exchange":
        MARKET_FOREX,

    "foreign-exchange":
        MARKET_FOREX,

    "future":
        MARKET_FUTURES,

    "futures":
        MARKET_FUTURES,

    "option":
        MARKET_OPTIONS,

    "options":
        MARKET_OPTIONS,

    "bond":
        MARKET_FIXED_INCOME,

    "bonds":
        MARKET_FIXED_INCOME,

    "fixed_income":
        MARKET_FIXED_INCOME,

    "fixed-income":
        MARKET_FIXED_INCOME,

    "commodity":
        MARKET_COMMODITIES,

    "commodities":
        MARKET_COMMODITIES,

    "multi_asset":
        MARKET_MULTI_ASSET,

    "multi-asset":
        MARKET_MULTI_ASSET,

    "multiasset":
        MARKET_MULTI_ASSET,
}


_MATRIX_PATH = (
    Path(__file__).with_name(
        "market_matrix.json"
    )
)


@lru_cache(maxsize=1)
def _market_matrix_by_name() -> dict[str, dict[str, Any]]:
    """
    Load the qualified 361-strategy market matrix.

    This data controls library filtering only.

    It does not authorize model inference, training, promotion,
    portfolio mutation, broker actions, or execution.
    """

    payload = json.loads(
        _MATRIX_PATH.read_text(
            encoding="utf-8"
        )
    )

    records = payload.get(
        "records"
    )

    if not isinstance(
        records,
        list,
    ):
        raise RuntimeError(
            "Strategy market matrix records are invalid."
        )

    if len(
        records
    ) != 361:
        raise RuntimeError(
            "Strategy market matrix must contain exactly 361 rows."
        )

    result: dict[str, dict[str, Any]] = {}

    for record in records:

        if not isinstance(
            record,
            dict,
        ):
            raise RuntimeError(
                "Strategy market matrix contains a non-object row."
            )

        name = str(
            record.get(
                "strategy_name"
            )
            or ""
        ).strip()

        if not name:
            raise RuntimeError(
                "Strategy market matrix contains an unnamed row."
            )

        if name in result:
            raise RuntimeError(
                "Duplicate strategy in market matrix: "
                + name
            )

        result[
            name
        ] = record

    return result


def _strategy_name(
    row: dict[str, Any],
) -> str:

    return str(
        row.get(
            "strategy_name"
        )
        or ""
    ).strip()


def _matrix_record(
    row: dict[str, Any],
) -> dict[str, Any] | None:

    name = _strategy_name(
        row
    )

    if not name:
        return None

    return (
        _market_matrix_by_name()
        .get(
            name
        )
    )


def _normalize_market(
    market: str | None,
) -> str:

    requested = str(
        market
        or ""
    ).strip().lower()

    requested = (
        requested
        .replace(
            " ",
            "_",
        )
    )

    return MARKET_ALIASES.get(
        requested,
        requested,
    )


def reference_strategy_market_hints(
    row: dict[str, Any],
) -> list[str]:
    """
    Return authoritative specific-market applicability.

    Unlike the previous implementation, an unclassified or portable
    strategy is NOT automatically returned for every requested market.

    cross_market is not a specific-market wildcard.
    """

    record = _matrix_record(
        row
    )

    if record is None:
        return []

    markets = record.get(
        "market_applicability"
    )

    if not isinstance(
        markets,
        list,
    ):
        return []

    return sorted({
        str(
            value
        ).strip()
        for value
        in markets
        if str(
            value
        ).strip()
    })


def strategy_matches_market_filter(
    row: dict[str, Any],
    market: str | None,
) -> bool:
    """
    Match only explicit matrix membership.

    Empty / "all" returns the full 361-strategy library.

    A specific market returns only strategies whose authoritative
    matrix row contains that specific market.
    """

    requested = _normalize_market(
        market
    )

    if (
        not requested
        or requested == "all"
    ):
        return True

    if requested not in SUPPORTED_MARKETS:
        return False

    hints = set(
        reference_strategy_market_hints(
            row
        )
    )

    return (
        requested
        in hints
    )


def enrich_reference_strategy(
    row: dict[str, Any],
) -> dict[str, Any]:
    """
    Add market-selection metadata to a catalog strategy.
    """

    result = dict(
        row
    )

    record = _matrix_record(
        row
    )

    result[
        "market_applicability"
    ] = (
        reference_strategy_market_hints(
            row
        )
    )

    result[
        "portable_across_markets"
    ] = bool(
        record
        and record.get(
            "portable_across_markets"
        )
        is True
    )

    result[
        "market_classification_pending"
    ] = bool(
        record
        and record.get(
            "needs_manual_review"
        )
        is True
    )

    return result
