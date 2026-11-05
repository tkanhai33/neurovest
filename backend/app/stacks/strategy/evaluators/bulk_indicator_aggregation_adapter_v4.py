"""Offline aggregation adapter for the fourth fifteen-strategy batch.

This module evaluates only the isolated V4 evaluator mapping and passes
its canonical result dictionaries directly to the existing aggregation
contract. It performs no registry, service, provider, database, portfolio,
order, or execution work.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from backend.app.stacks.strategy.evaluators.aggregation import (
    aggregate_strategy_results,
)
from backend.app.stacks.strategy.evaluators.bulk_indicator_family_v4 import (
    BULK_OFFLINE_EVALUATORS_V4,
)


Bar = Mapping[str, Any]
Result = dict[str, object]


def evaluate_bulk_indicator_batch_v4(
    bars: Sequence[Bar],
) -> tuple[Result, ...]:
    """Evaluate all fifteen offline strategies in qualified stable order."""

    return tuple(
        evaluator(bars)
        for evaluator in BULK_OFFLINE_EVALUATORS_V4.values()
    )


def aggregate_bulk_indicator_batch_v4(
    bars: Sequence[Bar],
) -> dict[str, object]:
    """Aggregate the exact canonical results from all fifteen evaluators."""

    results = evaluate_bulk_indicator_batch_v4(bars)

    return aggregate_strategy_results(results)


def healthcheck() -> dict[str, object]:
    """Expose the explicit offline-only boundary."""

    return {
        "status": "ok",
        "strategy_count": len(BULK_OFFLINE_EVALUATORS_V4),
        "aggregation_entrypoint":
            "aggregate_strategy_results",
        "offline_only": True,
        "registry_activated": False,
        "execution_enabled": False,
    }
