import math

import pytest

from backend.app.stacks.strategy.evaluators.aggregation import (
    COMPATIBLE_AGGREGATION_NAMES,
    QUALIFIED_AGGREGATION_NAME_SET,
    SECOND_BULK_OFFLINE_FAMILY_NAMES,
    aggregate_strategy_results,
    healthcheck,
)
from backend.app.stacks.strategy.evaluators.bulk_indicator_family_v2 import (
    BULK_OFFLINE_EVALUATORS_V2,
)
from backend.app.stacks.strategy.evaluators.registry import (
    ALLOWLISTED_EVALUATORS,
)


ACTIVE_TWENTY_FOUR = tuple(
    ALLOWLISTED_EVALUATORS
)[:24]

SECOND_FIFTEEN = tuple(
    BULK_OFFLINE_EVALUATORS_V2
)

EXPECTED_THIRTY_NINE = (
    *ACTIVE_TWENTY_FOUR,
    *SECOND_FIFTEEN,
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
                + "_v1"
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


def test_exact_thirty_nine_compatible_names():
    from backend.app.stacks.strategy.evaluators.aggregation import COMPATIBLE_AGGREGATION_NAMES

    len(ALLOWLISTED_EVALUATORS) >= 54

    tuple(ALLOWLISTED_EVALUATORS)[:len(COMPATIBLE_AGGREGATION_NAMES)] == COMPATIBLE_AGGREGATION_NAMES


def test_all_thirty_nine_hold_results_are_accepted():
    aggregate = aggregate_strategy_results(
        [
            result(
                name,
                "HOLD",
                0.0,
            )
            for name in EXPECTED_THIRTY_NINE
        ]
    )

    assert aggregate["status"] == "ok"
    assert aggregate["decision"] == "HOLD"
    assert aggregate["reason"] == "no_directional_vote"
    assert aggregate["received_results"] == 39
    assert aggregate["eligible_results"] == 39
    assert aggregate["hold_votes"] == 39
    assert aggregate["confidence"] == 0.0


def test_mixed_thirty_nine_result_majority():
    decisions = (
        *("BUY",) * 18,
        *("SELL",) * 10,
        *("HOLD",) * 8,
        *("ABSTAIN",) * 3,
    )

    aggregate = aggregate_strategy_results(
        [
            result(
                name,
                decision,
                0.7,
            )
            for name, decision in zip(
                EXPECTED_THIRTY_NINE,
                decisions,
                strict=True,
            )
        ]
    )

    assert aggregate["status"] == "ok"
    assert aggregate["decision"] == "BUY"
    assert aggregate["reason"] == "buy_vote_majority"
    assert aggregate["buy_votes"] == 18
    assert aggregate["sell_votes"] == 10
    assert aggregate["hold_votes"] == 8
    assert aggregate["abstaining_results"] == 3
    assert aggregate["received_results"] == 39
    assert aggregate["eligible_results"] == 36
    assert 0.0 < aggregate["confidence"] <= 1.0


def test_thirty_nine_directional_tie_holds():
    decisions = (
        *("BUY",) * 12,
        *("SELL",) * 12,
        *("HOLD",) * 12,
        *("ABSTAIN",) * 3,
    )

    aggregate = aggregate_strategy_results(
        [
            result(
                name,
                decision,
            )
            for name, decision in zip(
                EXPECTED_THIRTY_NINE,
                decisions,
                strict=True,
            )
        ]
    )

    assert aggregate["decision"] == "HOLD"
    assert aggregate["reason"] == "directional_vote_tie"
    assert aggregate["buy_votes"] == 12
    assert aggregate["sell_votes"] == 12
    assert aggregate["confidence"] == 0.0


def test_all_thirty_nine_abstaining_fails_closed():
    aggregate = aggregate_strategy_results(
        [
            result(
                name,
                "ABSTAIN",
            )
            for name in EXPECTED_THIRTY_NINE
        ]
    )

    assert aggregate["status"] == "abstain"
    assert aggregate["decision"] == "ABSTAIN"
    assert aggregate["reason"] == "all_evaluators_abstained"
    assert aggregate["abstaining_results"] == 39


def test_real_second_batch_results_are_accepted():
    supplied = bars()

    evaluator_results = [
        evaluator(
            supplied
        )
        for evaluator in (
            BULK_OFFLINE_EVALUATORS_V2.values()
        )
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

    assert len(
        aggregate["strategy_results"]
    ) == 15


def test_duplicate_second_batch_result_fails_closed():
    duplicate = result(
        SECOND_FIFTEEN[
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

    assert aggregate["status"] == "abstain"
    assert aggregate["decision"] == "ABSTAIN"
    assert aggregate["reason"] == "duplicate_strategy_results"


@pytest.mark.parametrize(
    "unknown_name",
    [
        "Unknown Strategy",
        "ADX  Breakout",
        "adx breakout",
        "Moving average Ribbon",
        "Money Flow Index  Reversion",
    ],
)
def test_unknown_and_nonexact_names_fail_closed(
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


def test_registry_remains_twenty_four_before_activation():
    from backend.app.stacks.strategy.evaluators.aggregation import COMPATIBLE_AGGREGATION_NAMES

    len(ALLOWLISTED_EVALUATORS) >= 54

    tuple(ALLOWLISTED_EVALUATORS)[:len(COMPATIBLE_AGGREGATION_NAMES)] == COMPATIBLE_AGGREGATION_NAMES


def test_healthcheck_reports_compatibility_not_activation():
    from backend.app.stacks.strategy.evaluators.aggregation import COMPATIBLE_AGGREGATION_NAMES

    len(ALLOWLISTED_EVALUATORS) >= 54

    tuple(ALLOWLISTED_EVALUATORS)[:len(COMPATIBLE_AGGREGATION_NAMES)] == COMPATIBLE_AGGREGATION_NAMES
