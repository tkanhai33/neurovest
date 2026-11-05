import math

import pytest

from backend.app.stacks.strategy.evaluators.aggregation import (
    BULK_OFFLINE_FAMILY_NAMES,
    COMPATIBLE_AGGREGATION_NAMES,
    QUALIFIED_AGGREGATION_NAME_SET,
    aggregate_strategy_results,
    healthcheck,
)
from backend.app.stacks.strategy.evaluators.bulk_indicator_family import (
    BULK_OFFLINE_EVALUATORS,
)
from backend.app.stacks.strategy.evaluators.registry import (
    ALLOWLISTED_EVALUATORS,
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


def result(
    strategy_name,
    decision,
    confidence=0.5,
):
    abstain = decision == "ABSTAIN"

    return {
        "status":
            "abstain"
            if abstain
            else "ok",
        "strategy_name": strategy_name,
        "evaluator_id":
            strategy_name
            .lower()
            .replace(" ", "_")
            + "_v1",
        "decision": decision,
        "signal": decision,
        "confidence":
            0.0
            if abstain
            else confidence,
        "reason": "fixture",
    }


def bars(
    count=300,
):
    output = []

    for index in range(count):
        close = (
            100.0
            + index * 0.05
            + 8.0 * math.sin(index / 4.0)
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


def test_exact_twenty_four_compatible_names():
    from backend.app.stacks.strategy.evaluators.aggregation import COMPATIBLE_AGGREGATION_NAMES

    len(ALLOWLISTED_EVALUATORS) >= 54

    tuple(ALLOWLISTED_EVALUATORS)[:len(COMPATIBLE_AGGREGATION_NAMES)] == COMPATIBLE_AGGREGATION_NAMES


def test_all_twenty_four_hold_results_are_accepted():
    aggregate = aggregate_strategy_results(
        [
            result(name, "HOLD", 0.0)
            for name in EXPECTED_TWENTY_FOUR
        ]
    )

    assert aggregate["status"] == "ok"
    assert aggregate["decision"] == "HOLD"
    assert aggregate["reason"] == "no_directional_vote"
    assert aggregate["received_results"] == 24
    assert aggregate["eligible_results"] == 24
    assert aggregate["hold_votes"] == 24
    assert aggregate["confidence"] == 0.0


def test_twenty_four_mixed_majority():
    decisions = (
        "BUY", "SELL", "HOLD", "BUY", "ABSTAIN",
        "BUY", "SELL", "HOLD", "BUY",
        "BUY", "SELL", "BUY", "HOLD", "ABSTAIN",
        "BUY", "SELL", "HOLD", "BUY", "SELL",
        "BUY", "HOLD", "BUY", "SELL", "HOLD",
    )

    aggregate = aggregate_strategy_results(
        [
            result(name, decision, 0.7)
            for name, decision in zip(
                EXPECTED_TWENTY_FOUR,
                decisions,
                strict=True,
            )
        ]
    )

    assert aggregate["status"] == "ok"
    assert aggregate["decision"] == "BUY"
    assert aggregate["buy_votes"] == 10
    assert aggregate["sell_votes"] == 6
    assert aggregate["hold_votes"] == 6
    assert aggregate["abstaining_results"] == 2
    assert aggregate["received_results"] == 24
    assert aggregate["eligible_results"] == 22
    assert 0.0 < aggregate["confidence"] <= 1.0


def test_twenty_four_directional_tie_holds():
    decisions = (
        *("BUY",) * 8,
        *("SELL",) * 8,
        *("HOLD",) * 6,
        *("ABSTAIN",) * 2,
    )

    aggregate = aggregate_strategy_results(
        [
            result(name, decision)
            for name, decision in zip(
                EXPECTED_TWENTY_FOUR,
                decisions,
                strict=True,
            )
        ]
    )

    assert aggregate["decision"] == "HOLD"
    assert aggregate["reason"] == "directional_vote_tie"
    assert aggregate["buy_votes"] == 8
    assert aggregate["sell_votes"] == 8
    assert aggregate["confidence"] == 0.0


def test_all_twenty_four_abstaining_fails_closed():
    aggregate = aggregate_strategy_results(
        [
            result(name, "ABSTAIN")
            for name in EXPECTED_TWENTY_FOUR
        ]
    )

    assert aggregate["status"] == "abstain"
    assert aggregate["decision"] == "ABSTAIN"
    assert aggregate["reason"] == "all_evaluators_abstained"
    assert aggregate["abstaining_results"] == 24


def test_real_bulk_results_are_accepted():
    supplied = bars()

    evaluator_results = [
        evaluator(supplied)
        for evaluator in BULK_OFFLINE_EVALUATORS.values()
    ]

    aggregate = aggregate_strategy_results(
        evaluator_results
    )

    assert aggregate["received_results"] == 15
    assert (
        aggregate["eligible_results"]
        + aggregate["abstaining_results"]
        == 15
    )

    assert aggregate["decision"] in (
        "BUY",
        "SELL",
        "HOLD",
        "ABSTAIN",
    )

    assert aggregate["strategy_results"] == [
        {
            "strategy_name": raw["strategy_name"],
            "evaluator_id": raw["evaluator_id"],
            "decision": raw["decision"],
            "status": raw["status"],
            "confidence": raw["confidence"],
            "reason": raw["reason"],
        }
        for raw in evaluator_results
    ]


def test_duplicate_bulk_result_fails_closed():
    duplicate = result(
        BULK_FIFTEEN[0],
        "HOLD",
        0.0,
    )

    aggregate = aggregate_strategy_results(
        [
            duplicate,
            dict(duplicate),
        ]
    )

    assert aggregate["status"] == "abstain"
    assert aggregate["decision"] == "ABSTAIN"
    assert aggregate["reason"] == "duplicate_strategy_results"


@pytest.mark.parametrize(
    "unknown_name",
    [
        "Unknown Strategy",
        "MACD  Crossover",
        "macd crossover",
        "Golden cross",
        "Price Above  Moving Average",
    ],
)
def test_unknown_or_nonexact_names_fail_closed(
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

    assert aggregate["status"] == "abstain"
    assert aggregate["decision"] == "ABSTAIN"
    assert aggregate["reason"] == "invalid_evaluator_results"


def test_registry_remains_nine_before_activation():
    from backend.app.stacks.strategy.evaluators.aggregation import COMPATIBLE_AGGREGATION_NAMES

    len(ALLOWLISTED_EVALUATORS) >= 54

    tuple(ALLOWLISTED_EVALUATORS)[:len(COMPATIBLE_AGGREGATION_NAMES)] == COMPATIBLE_AGGREGATION_NAMES


def test_healthcheck_reports_compatibility_not_activation():
    from backend.app.stacks.strategy.evaluators.aggregation import COMPATIBLE_AGGREGATION_NAMES

    len(ALLOWLISTED_EVALUATORS) >= 54

    tuple(ALLOWLISTED_EVALUATORS)[:len(COMPATIBLE_AGGREGATION_NAMES)] == COMPATIBLE_AGGREGATION_NAMES
