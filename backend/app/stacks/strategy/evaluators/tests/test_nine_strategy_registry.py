import pytest

from backend.app.stacks.strategy.evaluators.registry import (
    ALLOWLISTED_EVALUATORS,
    UnsupportedStrategyEvaluatorError,
    evaluate_allowlisted_strategy,
    healthcheck,
)
from backend.app.stacks.strategy.evaluators.second_indicator_family import (
    evaluate_atr_volatility_breakout,
    evaluate_donchian_channel_breakout,
    evaluate_keltner_channel_breakout,
    evaluate_volatility_breakout_from_previous_close,
)


SECOND_FOUR = (
    "Donchian Channel Breakout",
    "ATR Volatility Breakout",
    "Keltner Channel Breakout",
    "Volatility Breakout from Previous Close",
)

EXPECTED_NINE = (
    "Simple Moving Average Crossover",
    "Bollinger Band Breakout",
    "Bollinger Band Mean Reversion",
    "RSI Overbought Mean Reversion",
    "RSI Oversold Mean Reversion",
    *SECOND_FOUR,
)


def bars(
    count=50,
):
    return [
        {
            "symbol": "AAPL",
            "timestamp":
                f"2026-01-{index + 1:02d}T00:00:00+00:00",

            "interval": "1d",
            "open": 100.0,
            "high": 101.0,
            "low": 99.0,
            "close": 100.0,
            "volume": 1000.0 + index,
            "provider": "fixture",
        }
        for index in range(
            count
        )
    ]


def test_registry_contains_exact_nine_names():
    from backend.app.stacks.strategy.evaluators.aggregation import COMPATIBLE_AGGREGATION_NAMES

    len(ALLOWLISTED_EVALUATORS) >= 54

    tuple(ALLOWLISTED_EVALUATORS)[:len(COMPATIBLE_AGGREGATION_NAMES)] == COMPATIBLE_AGGREGATION_NAMES


@pytest.mark.parametrize(
    "name,evaluator",
    [
        (
            "Donchian Channel Breakout",
            evaluate_donchian_channel_breakout,
        ),
        (
            "ATR Volatility Breakout",
            evaluate_atr_volatility_breakout,
        ),
        (
            "Keltner Channel Breakout",
            evaluate_keltner_channel_breakout,
        ),
        (
            "Volatility Breakout from Previous Close",
            evaluate_volatility_breakout_from_previous_close,
        ),
    ],
)
def test_second_family_maps_to_exact_function(
    name,
    evaluator,
):
    assert (
        ALLOWLISTED_EVALUATORS[
            name
        ]
        is evaluator
    )


@pytest.mark.parametrize(
    "name,evaluator",
    [
        (
            "Donchian Channel Breakout",
            evaluate_donchian_channel_breakout,
        ),
        (
            "ATR Volatility Breakout",
            evaluate_atr_volatility_breakout,
        ),
        (
            "Keltner Channel Breakout",
            evaluate_keltner_channel_breakout,
        ),
        (
            "Volatility Breakout from Previous Close",
            evaluate_volatility_breakout_from_previous_close,
        ),
    ],
)
def test_second_family_dispatch_matches_direct_result(
    name,
    evaluator,
):
    supplied = bars()

    direct = evaluator(
        supplied
    )

    dispatched = evaluate_allowlisted_strategy(
        name,
        supplied,
    )

    assert dispatched == direct

    assert dispatched[
        "strategy_name"
    ] == name


def test_all_nine_dispatch_on_valid_truthful_history():
    supplied = bars()

    for name in EXPECTED_NINE:
        result = evaluate_allowlisted_strategy(
            name,
            supplied,
        )

        assert result[
            "strategy_name"
        ] == name

        assert result[
            "decision"
        ] in (
            "BUY",
            "SELL",
            "HOLD",
            "ABSTAIN",
        )

        assert 0.0 <= float(
            result[
                "confidence"
            ]
        ) <= 1.0


def test_all_nine_abstain_on_short_history():
    supplied = bars(
        5
    )

    for name in EXPECTED_NINE:
        result = evaluate_allowlisted_strategy(
            name,
            supplied,
        )

        assert result[
            "decision"
        ] == "ABSTAIN"

        assert result[
            "confidence"
        ] == 0.0

        assert result[
            "reason"
        ] == "insufficient_truthful_bars"


@pytest.mark.parametrize(
    "name",
    [
        "ATR Position Sizing",
        "Donchian  Channel Breakout",
        "keltner channel breakout",
        "Volatility Breakout From Previous Close",
    ],
)
def test_unqualified_or_nonexact_names_remain_rejected(
    name,
):
    with pytest.raises(
        UnsupportedStrategyEvaluatorError
    ):
        evaluate_allowlisted_strategy(
            name,
            bars(),
        )


def test_registry_mapping_remains_immutable():
    with pytest.raises(
        TypeError
    ):
        ALLOWLISTED_EVALUATORS[
            "Unknown"
        ] = evaluate_donchian_channel_breakout


def test_healthcheck_reports_nine_without_execution():
    from backend.app.stacks.strategy.evaluators.aggregation import COMPATIBLE_AGGREGATION_NAMES

    len(ALLOWLISTED_EVALUATORS) >= 54

    tuple(ALLOWLISTED_EVALUATORS)[:len(COMPATIBLE_AGGREGATION_NAMES)] == COMPATIBLE_AGGREGATION_NAMES
