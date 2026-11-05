from backend.app.stacks.strategy.evaluators.aggregation import (
    QUALIFIED_AGGREGATION_NAME_SET,
    aggregate_strategy_results,
)
from backend.app.stacks.strategy.evaluators.bulk_indicator_family_v7 import (
    BULK_OFFLINE_EVALUATORS_V7,
    SEVENTH_FIFTEEN_OHLCV_NAMES,
)
from backend.app.stacks.strategy.evaluators.registry import ALLOWLISTED_EVALUATORS


def bars(count=253):
    return [
        {
            "open": 100.0 + index * 0.14,
            "high": 101.2 + index * 0.14,
            "low": 99.1 + index * 0.14,
            "close": 100.4 + index * 0.14,
            "volume": 1000.0 + index * 10.0,
        }
        for index in range(count)
    ]


def test_exact_one_hundred_fourteen_global_capabilities():
    assert len(ALLOWLISTED_EVALUATORS) >= 114
    assert len(set(ALLOWLISTED_EVALUATORS)) >= 114
    assert tuple(ALLOWLISTED_EVALUATORS)[99:114] == SEVENTH_FIFTEEN_OHLCV_NAMES
    assert len(QUALIFIED_AGGREGATION_NAME_SET) >= 114


def test_active_aggregation_accepts_seventh_fifteen():
    output = aggregate_strategy_results(
        tuple(evaluator(bars()) for evaluator in BULK_OFFLINE_EVALUATORS_V7.values())
    )

    assert output["received_results"] == 15
    assert output["eligible_results"] == 15
    assert output["execution_enabled"] is False
