from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any
import json


_CATALOG_PATH = Path(__file__).with_name("catalog.json")


@lru_cache(maxsize=1)
def load_reference_strategy_catalog() -> dict[str, Any]:
    """Load the immutable NeuroVest reference-strategy catalog."""

    payload = json.loads(
        _CATALOG_PATH.read_text(
            encoding="utf-8",
        )
    )

    if payload.get("execution_capability") is not False:
        raise RuntimeError(
            "Reference strategy catalog must not have execution capability."
        )

    strategies = payload.get(
        "strategies"
    )

    if not isinstance(strategies, list):
        raise RuntimeError(
            "Reference strategy catalog strategies must be a list."
        )

    if len(strategies) < 151:
        raise RuntimeError(
            "Reference strategy catalog contains fewer than 151 strategies."
        )

    return payload


def get_reference_strategies() -> tuple[dict[str, Any], ...]:
    payload = load_reference_strategy_catalog()

    return tuple(
        dict(item)
        for item in payload["strategies"]
    )


def get_reference_strategy(
    strategy_name: str,
) -> dict[str, Any] | None:

    needle = strategy_name.strip().casefold()

    for item in get_reference_strategies():

        if (
            str(
                item.get(
                    "strategy_name",
                    "",
                )
            )
            .strip()
            .casefold()
            == needle
        ):
            return dict(item)

    return None


def search_reference_strategies(
    query: str,
    *,
    limit: int = 20,
) -> tuple[dict[str, Any], ...]:

    needle = query.strip().casefold()

    if not needle:
        return tuple()

    matches = []

    for item in get_reference_strategies():

        searchable = " ".join(
            str(
                item.get(
                    key,
                    "",
                )
            )
            for key in (
                "strategy_name",
                "definition",
                "formula_or_rules",
                "best_suited_for",
                "category",
            )
        ).casefold()

        if needle in searchable:
            matches.append(
                dict(item)
            )

        if len(matches) >= limit:
            break

    return tuple(matches)
