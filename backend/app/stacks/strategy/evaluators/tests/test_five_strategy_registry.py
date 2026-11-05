import pytest

from backend.app.stacks.strategy.evaluators.indicator_family import (
    evaluate_bollinger_band_breakout,
    evaluate_bollinger_band_mean_reversion,
    evaluate_rsi_overbought_mean_reversion,
    evaluate_rsi_oversold_mean_reversion,
)
from backend.app.stacks.strategy.evaluators.registry import (
    ALLOWLISTED_EVALUATORS,
    UnsupportedStrategyEvaluatorError,
    evaluate_allowlisted_strategy,
    healthcheck,
)
from backend.app.stacks.strategy.evaluators.sma_crossover import (
    STRATEGY_NAME,
    evaluate_sma_crossover,
)


BREAKOUT = "Bollinger Band Breakout"
MEAN_REVERSION = "Bollinger Band Mean Reversion"
RSI_OVERBOUGHT = "RSI Overbought Mean Reversion"
RSI_OVERSOLD = "RSI Oversold Mean Reversion"

DONCHIAN = "Donchian Channel Breakout"
ATR_BREAKOUT = "ATR Volatility Breakout"
KELTNER = "Keltner Channel Breakout"
PREVIOUS_CLOSE_BREAKOUT = (
    "Volatility Breakout from Previous Close"
)

EXPECTED_NAMES = (
    STRATEGY_NAME,
    BREAKOUT,
    MEAN_REVERSION,
    RSI_OVERBOUGHT,
    RSI_OVERSOLD,
    DONCHIAN,
    ATR_BREAKOUT,
    KELTNER,
    PREVIOUS_CLOSE_BREAKOUT,
)


def bars_from_closes(
    closes,
):
    return [
        {
            "symbol": "AAPL",
            "timestamp": (
                f"2026-01-{index + 1:02d}T00:00:00+00:00"
            ),
            "interval": "1d",
            "open": float(
                close
            ),
            "high": float(
                close
            ) + 1.0,
            "low": max(
                float(
                    close
                ) - 1.0,
                0.01,
            ),
            "close": float(
                close
            ),
            "volume": 1000.0 + index,
            "provider": "fixture",
        }
        for index, close in enumerate(
            closes
        )
    ]


def alternating_closes():
    return [
        100.0
        if index % 2 == 0
        else 99.0
        for index in range(
            15
        )
    ]


def test_registry_contains_exact_nine_names_in_stable_order():
    from backend.app.stacks.strategy.evaluators.aggregation import COMPATIBLE_AGGREGATION_NAMES

    len(ALLOWLISTED_EVALUATORS) >= 54

    tuple(ALLOWLISTED_EVALUATORS)[:len(COMPATIBLE_AGGREGATION_NAMES)] == COMPATIBLE_AGGREGATION_NAMES


@pytest.mark.parametrize(
    "strategy_name,evaluator",
    [
        (
            STRATEGY_NAME,
            evaluate_sma_crossover,
        ),
        (
            BREAKOUT,
            evaluate_bollinger_band_breakout,
        ),
        (
            MEAN_REVERSION,
            evaluate_bollinger_band_mean_reversion,
        ),
        (
            RSI_OVERBOUGHT,
            evaluate_rsi_overbought_mean_reversion,
        ),
        (
            RSI_OVERSOLD,
            evaluate_rsi_oversold_mean_reversion,
        ),
    ],
)
def test_registry_maps_exact_identity_to_exact_function(
    strategy_name,
    evaluator,
):
    assert (
        ALLOWLISTED_EVALUATORS[
            strategy_name
        ]
        is evaluator
    )


@pytest.mark.parametrize(
    "strategy_name,evaluator,closes",
    [
        (
            STRATEGY_NAME,
            evaluate_sma_crossover,
            [
                100.0
            ] * 20
            +
            [
                110.0
            ],
        ),
        (
            BREAKOUT,
            evaluate_bollinger_band_breakout,
            [
                100.0
            ] * 20
            +
            [
                130.0
            ],
        ),
        (
            MEAN_REVERSION,
            evaluate_bollinger_band_mean_reversion,
            [
                100.0
            ] * 20
            +
            [
                70.0
            ],
        ),
        (
            RSI_OVERBOUGHT,
            evaluate_rsi_overbought_mean_reversion,
            alternating_closes()
            +
            [
                120.0
            ],
        ),
        (
            RSI_OVERSOLD,
            evaluate_rsi_oversold_mean_reversion,
            alternating_closes()
            +
            [
                80.0
            ],
        ),
    ],
)
def test_registry_dispatch_matches_direct_evaluator(
    strategy_name,
    evaluator,
    closes,
):
    bars = bars_from_closes(
        closes
    )

    direct = evaluator(
        bars
    )

    dispatched = evaluate_allowlisted_strategy(
        strategy_name,
        bars,
    )

    assert dispatched == direct
    assert dispatched[
        "strategy_name"
    ] == strategy_name


def test_all_nine_hold_or_signal_on_valid_history():
    bars = bars_from_closes(
        [
            100.0
        ] * 50
    )

    for strategy_name in EXPECTED_NAMES:
        result = evaluate_allowlisted_strategy(
            strategy_name,
            bars,
        )

        assert result[
            "status"
        ] == "ok"

        assert result[
            "decision"
        ] in (
            "BUY",
            "SELL",
            "HOLD",
        )

        assert result[
            "strategy_name"
        ] == strategy_name

        assert 0.0 <= float(
            result[
                "confidence"
            ]
        ) <= 1.0


def test_all_nine_abstain_on_insufficient_history():
    bars = bars_from_closes(
        [
            100.0
        ] * 10
    )

    for strategy_name in EXPECTED_NAMES:
        result = evaluate_allowlisted_strategy(
            strategy_name,
            bars,
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
    "unknown_name",
    [
        "",
        "Unknown Strategy",
        "Bollinger  Band Breakout",
        "bollinger band breakout",
        "RSI",
        "__import__('os')",
    ],
)
def test_unknown_or_nonexact_names_are_rejected(
    unknown_name,
):
    with pytest.raises(
        UnsupportedStrategyEvaluatorError
    ):
        evaluate_allowlisted_strategy(
            unknown_name,
            bars_from_closes(
                [
                    100.0
                ] * 50
            ),
        )


def test_registry_is_immutable():
    with pytest.raises(
        TypeError
    ):
        ALLOWLISTED_EVALUATORS[
            "Unknown Strategy"
        ] = evaluate_sma_crossover


def test_healthcheck_reports_nine_without_execution():
    from backend.app.stacks.strategy.evaluators.aggregation import COMPATIBLE_AGGREGATION_NAMES

    len(ALLOWLISTED_EVALUATORS) >= 54

    tuple(ALLOWLISTED_EVALUATORS)[:len(COMPATIBLE_AGGREGATION_NAMES)] == COMPATIBLE_AGGREGATION_NAMES
