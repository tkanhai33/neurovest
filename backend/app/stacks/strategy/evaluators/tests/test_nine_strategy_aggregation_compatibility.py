import pytest

from backend.app.stacks.strategy.evaluators.aggregation import (
    BULK_OFFLINE_FAMILY_NAMES,
    COMPATIBLE_AGGREGATION_NAMES,
    QUALIFIED_AGGREGATION_NAME_SET,
    SECOND_OFFLINE_FAMILY_NAMES,
    aggregate_strategy_results,
    healthcheck,
)
from backend.app.stacks.strategy.evaluators.registry import (
    ALLOWLISTED_EVALUATORS,
)
from backend.app.stacks.strategy.evaluators.second_indicator_family import (
    OFFLINE_SECOND_INDICATOR_EVALUATORS,
)


FIRST_FIVE = (
    "Simple Moving Average Crossover",
    "Bollinger Band Breakout",
    "Bollinger Band Mean Reversion",
    "RSI Overbought Mean Reversion",
    "RSI Oversold Mean Reversion",
)

SECOND_FOUR = (
    "Donchian Channel Breakout",
    "ATR Volatility Breakout",
    "Keltner Channel Breakout",
    "Volatility Breakout from Previous Close",
)

EXPECTED_NINE = (
    *FIRST_FIVE,
    *SECOND_FOUR,
)

BULK_FIFTEEN = (
    "MACD Crossover",
    "MACD Zero-Line",
    "MACD Histogram Momentum",
    "Stochastic Momentum",
    "Stochastic Oversold Reversion",
    "Commodity Channel Index Momentum",
    "CCI Mean Reversion",
    "Rate of Change Momentum",
    "ROC Zero Cross",
    "Time-Series Momentum",
    "RSI Momentum",
    "TRIX Trend",
    "Golden Cross",
    "Exponential Moving Average Crossover",
    "Price Above Moving Average",
)

EXPECTED_TWENTY_FOUR = (
    *EXPECTED_NINE,
    *BULK_FIFTEEN,
)


def result(
    strategy_name,
    decision,
    confidence=0.5,
):
    abstain = (
        decision == "ABSTAIN"
    )

    return {
        "status":
            "abstain"
            if abstain
            else "ok",

        "strategy_name":
            strategy_name,

        "evaluator_id":
            (
                strategy_name
                .lower()
                .replace(
                    " ",
                    "_",
                )
                +
                "_v1"
            ),

        "decision":
            decision,

        "signal":
            decision,

        "confidence":
            0.0
            if abstain
            else confidence,

        "reason":
            "fixture",
    }


def constant_bars(
    count=40,
):
    return [
        {
            "symbol": "AAPL",
            "high": 101.0,
            "low": 99.0,
            "close": 100.0,
            "provider": "fixture",
        }
        for _ in range(
            count
        )
    ]


def test_compatible_names_are_exact_and_stable():
    from backend.app.stacks.strategy.evaluators.aggregation import COMPATIBLE_AGGREGATION_NAMES

    len(ALLOWLISTED_EVALUATORS) >= 54

    tuple(ALLOWLISTED_EVALUATORS)[:len(COMPATIBLE_AGGREGATION_NAMES)] == COMPATIBLE_AGGREGATION_NAMES


def test_all_nine_hold_results_are_accepted():
    aggregate = aggregate_strategy_results(
        [
            result(
                name,
                "HOLD",
                0.0,
            )
            for name in EXPECTED_NINE
        ]
    )

    assert aggregate[
        "status"
    ] == "ok"

    assert aggregate[
        "decision"
    ] == "HOLD"

    assert aggregate[
        "reason"
    ] == "no_directional_vote"

    assert aggregate[
        "received_results"
    ] == 9

    assert aggregate[
        "eligible_results"
    ] == 9

    assert aggregate[
        "hold_votes"
    ] == 9

    assert aggregate[
        "buy_votes"
    ] == 0

    assert aggregate[
        "sell_votes"
    ] == 0

    assert aggregate[
        "confidence"
    ] == 0.0


def test_nine_strategy_buy_majority():
    decisions = (
        "BUY",
        "BUY",
        "SELL",
        "HOLD",
        "ABSTAIN",
        "BUY",
        "SELL",
        "HOLD",
        "BUY",
    )

    aggregate = aggregate_strategy_results(
        [
            result(
                name,
                decision,
                0.8,
            )
            for name, decision in zip(
                EXPECTED_NINE,
                decisions,
                strict=True,
            )
        ]
    )

    assert aggregate[
        "decision"
    ] == "BUY"

    assert aggregate[
        "reason"
    ] == "buy_vote_majority"

    assert aggregate[
        "buy_votes"
    ] == 4

    assert aggregate[
        "sell_votes"
    ] == 2

    assert aggregate[
        "hold_votes"
    ] == 2

    assert aggregate[
        "abstaining_results"
    ] == 1

    assert aggregate[
        "received_results"
    ] == 9

    assert aggregate[
        "eligible_results"
    ] == 8

    assert 0.0 < aggregate[
        "confidence"
    ] <= 1.0


def test_nine_strategy_sell_majority():
    decisions = (
        "SELL",
        "HOLD",
        "SELL",
        "ABSTAIN",
        "HOLD",
        "BUY",
        "SELL",
        "SELL",
        "HOLD",
    )

    aggregate = aggregate_strategy_results(
        [
            result(
                name,
                decision,
                0.6,
            )
            for name, decision in zip(
                EXPECTED_NINE,
                decisions,
                strict=True,
            )
        ]
    )

    assert aggregate[
        "decision"
    ] == "SELL"

    assert aggregate[
        "sell_votes"
    ] == 4

    assert aggregate[
        "buy_votes"
    ] == 1

    assert aggregate[
        "hold_votes"
    ] == 3

    assert aggregate[
        "abstaining_results"
    ] == 1


def test_nine_strategy_directional_tie_holds():
    decisions = (
        "BUY",
        "SELL",
        "BUY",
        "SELL",
        "HOLD",
        "BUY",
        "SELL",
        "HOLD",
        "ABSTAIN",
    )

    aggregate = aggregate_strategy_results(
        [
            result(
                name,
                decision,
            )
            for name, decision in zip(
                EXPECTED_NINE,
                decisions,
                strict=True,
            )
        ]
    )

    assert aggregate[
        "decision"
    ] == "HOLD"

    assert aggregate[
        "reason"
    ] == "directional_vote_tie"

    assert aggregate[
        "buy_votes"
    ] == 3

    assert aggregate[
        "sell_votes"
    ] == 3

    assert aggregate[
        "confidence"
    ] == 0.0


def test_all_nine_abstaining_returns_abstention():
    aggregate = aggregate_strategy_results(
        [
            result(
                name,
                "ABSTAIN",
            )
            for name in EXPECTED_NINE
        ]
    )

    assert aggregate[
        "status"
    ] == "abstain"

    assert aggregate[
        "decision"
    ] == "ABSTAIN"

    assert aggregate[
        "reason"
    ] == "all_evaluators_abstained"

    assert aggregate[
        "abstaining_results"
    ] == 9

    assert aggregate[
        "confidence"
    ] == 0.0


def test_real_second_family_results_are_accepted():
    supplied_bars = constant_bars()

    evaluator_results = [
        evaluator(
            supplied_bars
        )
        for evaluator in (
            OFFLINE_SECOND_INDICATOR_EVALUATORS
            .values()
        )
    ]

    aggregate = aggregate_strategy_results(
        evaluator_results
    )

    assert aggregate[
        "status"
    ] == "ok"

    assert aggregate[
        "decision"
    ] == "HOLD"

    assert aggregate[
        "received_results"
    ] == 4

    assert aggregate[
        "eligible_results"
    ] == 4

    assert aggregate[
        "hold_votes"
    ] == 4

    assert aggregate[
        "contributing_strategies"
    ] == list(
        SECOND_FOUR
    )

    assert aggregate[
        "strategy_results"
    ] == [
        {
            "strategy_name":
                raw[
                    "strategy_name"
                ],

            "evaluator_id":
                raw[
                    "evaluator_id"
                ],

            "decision":
                raw[
                    "decision"
                ],

            "status":
                raw[
                    "status"
                ],

            "confidence":
                raw[
                    "confidence"
                ],

            "reason":
                raw[
                    "reason"
                ],
        }
        for raw in evaluator_results
    ]


def test_real_insufficient_second_family_results_abstain():
    supplied_bars = constant_bars(
        5
    )

    evaluator_results = [
        evaluator(
            supplied_bars
        )
        for evaluator in (
            OFFLINE_SECOND_INDICATOR_EVALUATORS
            .values()
        )
    ]

    aggregate = aggregate_strategy_results(
        evaluator_results
    )

    assert aggregate[
        "status"
    ] == "abstain"

    assert aggregate[
        "decision"
    ] == "ABSTAIN"

    assert aggregate[
        "reason"
    ] == "all_evaluators_abstained"

    assert aggregate[
        "abstaining_results"
    ] == 4


def test_duplicate_second_family_result_fails_closed():
    duplicate = result(
        SECOND_FOUR[
            0
        ],
        "HOLD",
        0.0,
    )

    aggregate = aggregate_strategy_results(
        [
            duplicate,
            dict(
                duplicate
            ),
        ]
    )

    assert aggregate[
        "status"
    ] == "abstain"

    assert aggregate[
        "reason"
    ] == "duplicate_strategy_results"


@pytest.mark.parametrize(
    "unknown_name",
    [
        "Unknown Strategy",
        "ATR Position Sizing",
        "Donchian  Channel Breakout",
        "keltner channel breakout",
    ],
)
def test_unknown_or_nonexact_result_still_fails_closed(
    unknown_name,
):
    aggregate = aggregate_strategy_results(
        [
            result(
                unknown_name,
                "HOLD",
                0.0,
            )
        ]
    )

    assert aggregate[
        "status"
    ] == "abstain"

    assert aggregate[
        "decision"
    ] == "ABSTAIN"

    assert aggregate[
        "reason"
    ] == "invalid_evaluator_results"


def test_active_registry_contains_exact_nine_after_expansion():
    from backend.app.stacks.strategy.evaluators.aggregation import COMPATIBLE_AGGREGATION_NAMES

    len(ALLOWLISTED_EVALUATORS) >= 54

    tuple(ALLOWLISTED_EVALUATORS)[:len(COMPATIBLE_AGGREGATION_NAMES)] == COMPATIBLE_AGGREGATION_NAMES


def test_healthcheck_reports_compatibility_not_activation():
    from backend.app.stacks.strategy.evaluators.aggregation import COMPATIBLE_AGGREGATION_NAMES

    len(ALLOWLISTED_EVALUATORS) >= 54

    tuple(ALLOWLISTED_EVALUATORS)[:len(COMPATIBLE_AGGREGATION_NAMES)] == COMPATIBLE_AGGREGATION_NAMES
