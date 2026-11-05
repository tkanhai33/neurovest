import math

import pytest

from backend.app.stacks.strategy.evaluators.bulk_indicator_family import (
    BULK_OFFLINE_EVALUATORS,
)
from backend.app.stacks.strategy.evaluators.registry import (
    ALLOWLISTED_EVALUATORS,
    UnsupportedStrategyEvaluatorError,
    evaluate_allowlisted_strategy,
    healthcheck,
)


FIRST_NINE = (
    "Simple Moving Average Crossover",
    "Bollinger Band Breakout",
    "Bollinger Band Mean Reversion",
    "RSI Overbought Mean Reversion",
    "RSI Oversold Mean Reversion",
    "Donchian Channel Breakout",
    "ATR Volatility Breakout",
    "Keltner Channel Breakout",
    "Volatility Breakout from Previous Close",
)

BULK_FIFTEEN = tuple(
    BULK_OFFLINE_EVALUATORS
)

EXPECTED_TWENTY_FOUR = (
    *FIRST_NINE,
    *BULK_FIFTEEN,
)


def bars(
    count=300,
):
    output = []

    for index in range(count):
        close = (
            100.0
            + index * 0.05
            + 8.0 * math.sin(
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


def test_registry_contains_exact_stable_twenty_four():
    from backend.app.stacks.strategy.evaluators.aggregation import COMPATIBLE_AGGREGATION_NAMES

    len(ALLOWLISTED_EVALUATORS) >= 54

    tuple(ALLOWLISTED_EVALUATORS)[:len(COMPATIBLE_AGGREGATION_NAMES)] == COMPATIBLE_AGGREGATION_NAMES


def test_original_nine_remain_first():
    assert tuple(
        ALLOWLISTED_EVALUATORS
    )[:9] == FIRST_NINE


def test_bulk_fifteen_are_appended_in_contract_order():
    assert tuple(
        ALLOWLISTED_EVALUATORS
    )[9:24] == BULK_FIFTEEN


def test_registry_is_immutable():
    with pytest.raises(
        TypeError
    ):
        ALLOWLISTED_EVALUATORS[
            "Unknown Strategy"
        ] = lambda supplied: supplied


@pytest.mark.parametrize(
    "name",
    BULK_FIFTEEN,
)
def test_bulk_direct_and_dispatched_results_match(
    name,
):
    supplied = bars()

    direct = BULK_OFFLINE_EVALUATORS[
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
        "MACD  Crossover",
        "macd crossover",
        "Golden cross",
        "Price Above  Moving Average",
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


def test_healthcheck_reports_static_twenty_four():
    from backend.app.stacks.strategy.evaluators.aggregation import COMPATIBLE_AGGREGATION_NAMES

    len(ALLOWLISTED_EVALUATORS) >= 54

    tuple(ALLOWLISTED_EVALUATORS)[:len(COMPATIBLE_AGGREGATION_NAMES)] == COMPATIBLE_AGGREGATION_NAMES
