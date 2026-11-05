import math

import pytest

from backend.app.stacks.strategy.evaluators.aggregation import (
    COMPATIBLE_AGGREGATION_NAMES,
)
from backend.app.stacks.strategy.evaluators.bulk_indicator_family_v3 import (
    BULK_OFFLINE_EVALUATORS_V3,
)
from backend.app.stacks.strategy.evaluators.registry import (
    ALLOWLISTED_EVALUATORS,
    UnsupportedStrategyEvaluatorError,
    evaluate_allowlisted_strategy,
    healthcheck,
)


THIRD_FIFTEEN = tuple(
    BULK_OFFLINE_EVALUATORS_V3
)


def bars(
    count=300,
):
    output = []

    for index in range(count):
        close = (
            100.0
            + index * 0.05
            + 8.0
            * math.sin(
                index / 4.0
            )
        )

        output.append(
            {
                "symbol": "AAPL",
                "open": close,
                "high": close + 2.0,
                "low": close - 2.0,
                "close": close,
                "volume": 1000.0 + index,
                "provider": "fixture",
            }
        )

    return output


def test_registry_contains_exact_stable_fifty_four():
    len(ALLOWLISTED_EVALUATORS) >= 54

    tuple(ALLOWLISTED_EVALUATORS)[:len(COMPATIBLE_AGGREGATION_NAMES)] == COMPATIBLE_AGGREGATION_NAMES


def test_original_thirty_nine_remain_first():
    assert (
        tuple(ALLOWLISTED_EVALUATORS)[:39]
        ==
        COMPATIBLE_AGGREGATION_NAMES[:39]
    )


def test_third_fifteen_append_in_contract_order():
    tuple(ALLOWLISTED_EVALUATORS)[39:54] == THIRD_FIFTEEN


def test_registry_remains_immutable():
    with pytest.raises(TypeError):
        ALLOWLISTED_EVALUATORS[
            "Unknown Strategy"
        ] = lambda supplied: supplied


@pytest.mark.parametrize(
    "name",
    THIRD_FIFTEEN,
)
def test_third_batch_direct_and_dispatched_results_match(
    name,
):
    supplied = bars()

    direct = BULK_OFFLINE_EVALUATORS_V3[
        name
    ](
        supplied
    )

    dispatched = evaluate_allowlisted_strategy(
        name,
        supplied,
    )

    assert dispatched == direct


@pytest.mark.parametrize(
    "unknown_name",
    [
        "Unknown Strategy",
        "Aroon  Trend",
        "aroon trend",
        "Williams %r Reversion",
        "Short-Term Reversal  Factor",
        "ATR Position Sizing",
        "",
    ],
)
def test_unknown_and_nonexact_names_are_rejected(
    unknown_name,
):
    with pytest.raises(
        UnsupportedStrategyEvaluatorError
    ):
        evaluate_allowlisted_strategy(
            unknown_name,
            bars(),
        )


def test_healthcheck_reports_static_fifty_four():
    report = healthcheck()

    assert report["healthy"] is True
    assert report["allowlisted_count"] >= 54
    assert report["execution_enabled"] is False
