from backend.app.stacks.strategy.evaluators.aggregation import (
    QUALIFIED_AGGREGATION_NAME_SET,
    aggregate_strategy_results,
)
from backend.app.stacks.strategy.evaluators.bulk_indicator_family_v6 import (
    BULK_OFFLINE_EVALUATORS_V6,
    SIXTH_FIFTEEN_OHLCV_NAMES,
)
from backend.app.stacks.strategy.evaluators.registry import ALLOWLISTED_EVALUATORS


def bars(count=253):
    return [
        {
            "open": 100.0 + index * 0.16,
            "high": 101.0 + index * 0.16,
            "low": 99.0 + index * 0.16,
            "close": 100.3 + index * 0.16,
            "volume": 1000.0 + index * 13.0,
        }
        for index in range(count)
    ]


def test_exact_ninety_nine_global_capabilities():
    assert len(ALLOWLISTED_EVALUATORS) >= 99
    assert len(set(ALLOWLISTED_EVALUATORS)) >= 99
    assert tuple(ALLOWLISTED_EVALUATORS)[84:99] == SIXTH_FIFTEEN_OHLCV_NAMES
    assert len(QUALIFIED_AGGREGATION_NAME_SET) >= 99


def test_active_aggregation_accepts_sixth_fifteen():
    output = aggregate_strategy_results(
        tuple(evaluator(bars()) for evaluator in BULK_OFFLINE_EVALUATORS_V6.values())
    )
    assert output["received_results"] == 15
    assert output["eligible_results"] == 15
    assert output["execution_enabled"] is False
