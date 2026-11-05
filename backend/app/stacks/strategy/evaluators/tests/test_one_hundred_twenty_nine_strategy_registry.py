from backend.app.stacks.strategy.evaluators.aggregation import (
    QUALIFIED_AGGREGATION_NAME_SET,
    aggregate_strategy_results,
)
from backend.app.stacks.strategy.evaluators.bulk_indicator_family_v8 import (
    BULK_OFFLINE_EVALUATORS_V8,
    EIGHTH_FIFTEEN_STRICT_OHLCV_NAMES,
)
from backend.app.stacks.strategy.evaluators.registry import ALLOWLISTED_EVALUATORS


def bars(count=253):
    return [
        {
            "open": 100.0 + index * 0.15,
            "high": 101.3 + index * 0.15,
            "low": 99.2 + index * 0.15,
            "close": 100.5 + index * 0.15,
            "volume": 1000.0 + index * 12.0,
        }
        for index in range(count)
    ]


def test_exact_one_hundred_twenty_nine_global_capabilities():
    assert len(ALLOWLISTED_EVALUATORS) >= 129
    assert len(set(ALLOWLISTED_EVALUATORS)) >= 129
    assert tuple(ALLOWLISTED_EVALUATORS)[114:129] == EIGHTH_FIFTEEN_STRICT_OHLCV_NAMES
    assert len(QUALIFIED_AGGREGATION_NAME_SET) >= 129


def test_active_aggregation_accepts_eighth_fifteen():
    output = aggregate_strategy_results(
        tuple(evaluator(bars()) for evaluator in BULK_OFFLINE_EVALUATORS_V8.values())
    )

    assert output["received_results"] == 15
    assert output["eligible_results"] == 15
    assert output["execution_enabled"] is False
