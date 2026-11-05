from __future__ import annotations

from backend.app.stacks.strategy.evaluators.aggregation import (
    QUALIFIED_AGGREGATION_NAME_SET,
    aggregate_strategy_results,
)
from backend.app.stacks.strategy.evaluators.bulk_indicator_family_v4 import (
    BULK_OFFLINE_EVALUATORS_V4,
)
from backend.app.stacks.strategy.evaluators.bulk_indicator_strategy_contracts_v4 import (
    BULK_INDICATOR_STRATEGY_CONTRACTS_V4,
)
from backend.app.stacks.strategy.evaluators.registry import (
    ALLOWLISTED_EVALUATORS,
)


V4_NAMES = tuple(
    contract.strategy_name
    for contract in BULK_INDICATOR_STRATEGY_CONTRACTS_V4
)


def bars(count=140):
    return [
        {
            "open": 100.0 + index * 0.05,
            "high": 101.0 + index * 0.05,
            "low": 99.0 + index * 0.05,
            "close": 100.0 + index * 0.05,
            "volume": 1000.0 + index,
        }
        for index in range(count)
    ]


def test_exact_sixty_nine_global_capabilities():
    assert len(ALLOWLISTED_EVALUATORS) >= 69
    assert len(set(ALLOWLISTED_EVALUATORS)) >= 69
    assert tuple(ALLOWLISTED_EVALUATORS)[54:69] == V4_NAMES
    assert len(QUALIFIED_AGGREGATION_NAME_SET) >= 69
    assert set(V4_NAMES) <= QUALIFIED_AGGREGATION_NAME_SET


def test_active_aggregation_accepts_qualified_v4_results():
    results = tuple(
        evaluator(bars())
        for evaluator in BULK_OFFLINE_EVALUATORS_V4.values()
    )

    output = aggregate_strategy_results(results)

    assert output["status"] == "ok"
    assert output["received_results"] == 15
    assert output["eligible_results"] == 15
    assert output["decision"] in {"BUY", "SELL", "HOLD", "ABSTAIN"}
    assert output["execution_enabled"] is False
