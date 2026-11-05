from backend.app.stacks.strategy.evaluators.aggregation import (
    QUALIFIED_AGGREGATION_NAME_SET,
    aggregate_strategy_results,
)
from backend.app.stacks.strategy.evaluators.bulk_indicator_family_v5 import (
    BULK_OFFLINE_EVALUATORS_V5,
    FIFTH_FIFTEEN_OHLCV_NAMES,
)
from backend.app.stacks.strategy.evaluators.registry import ALLOWLISTED_EVALUATORS


def bars(count=253):
    return [
        {
            "open": 100.0 + index * 0.12,
            "high": 101.0 + index * 0.12,
            "low": 99.0 + index * 0.12,
            "close": 100.2 + index * 0.12,
            "volume": 1000.0 + index * 11.0,
        }
        for index in range(count)
    ]


def test_exact_eighty_four_global_capabilities():
    assert len(ALLOWLISTED_EVALUATORS) >= 84
    assert len(set(ALLOWLISTED_EVALUATORS)) >= 84
    assert tuple(ALLOWLISTED_EVALUATORS)[69:84] == FIFTH_FIFTEEN_OHLCV_NAMES
    assert len(QUALIFIED_AGGREGATION_NAME_SET) >= 84


def test_active_aggregation_accepts_fifth_fifteen():
    output = aggregate_strategy_results(
        tuple(evaluator(bars()) for evaluator in BULK_OFFLINE_EVALUATORS_V5.values())
    )
    assert output["received_results"] == 15
    assert output["eligible_results"] == 15
    assert output["execution_enabled"] is False
