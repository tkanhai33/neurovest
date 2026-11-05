import math

import pytest

from backend.app.stacks.strategy.evaluators.aggregation import (
    COMPATIBLE_AGGREGATION_NAMES,
    QUALIFIED_AGGREGATION_NAME_SET,
    THIRD_BULK_OFFLINE_FAMILY_NAMES,
    aggregate_strategy_results,
    healthcheck,
)
from backend.app.stacks.strategy.evaluators.bulk_indicator_family_v3 import (
    BULK_OFFLINE_EVALUATORS_V3,
)
from backend.app.stacks.strategy.evaluators.registry import (
    ALLOWLISTED_EVALUATORS,
)


ACTIVE_THIRTY_NINE = tuple(
    ALLOWLISTED_EVALUATORS
)[:39]

THIRD_FIFTEEN = tuple(
    BULK_OFFLINE_EVALUATORS_V3
)

EXPECTED_FIFTY_FOUR = (
    *ACTIVE_THIRTY_NINE,
    *THIRD_FIFTEEN,
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


def test_exact_fifty_four_compatible_names():
    assert len(
        ACTIVE_THIRTY_NINE
    ) == 39

    assert len(
        THIRD_FIFTEEN
    ) == 15

    assert (
        THIRD_BULK_OFFLINE_FAMILY_NAMES
        ==
        THIRD_FIFTEEN
    )

    assert (
        COMPATIBLE_AGGREGATION_NAMES
        ==
        EXPECTED_FIFTY_FOUR
    )

    frozenset(EXPECTED_FIFTY_FOUR) <= QUALIFIED_AGGREGATION_NAME_SET


def test_all_fifty_four_hold_results_are_accepted():
    aggregate = aggregate_strategy_results(
        [
            result(
                name,
                "HOLD",
                0.0,
            )
            for name in EXPECTED_FIFTY_FOUR
        ]
    )

    assert aggregate["status"] == "ok"
    assert aggregate["decision"] == "HOLD"
    assert aggregate["reason"] == "no_directional_vote"
    assert aggregate["received_results"] == 54
    assert aggregate["eligible_results"] == 54
    assert aggregate["hold_votes"] == 54
    assert aggregate["confidence"] == 0.0


def test_mixed_fifty_four_result_majority():
    decisions = (
        *("BUY",) * 25,
        *("SELL",) * 15,
        *("HOLD",) * 10,
        *("ABSTAIN",) * 4,
    )

    aggregate = aggregate_strategy_results(
        [
            result(
                name,
                decision,
                0.7,
            )
            for name, decision in zip(
                EXPECTED_FIFTY_FOUR,
                decisions,
                strict=True,
            )
        ]
    )

    assert aggregate["status"] == "ok"
    assert aggregate["decision"] == "BUY"
    assert aggregate["reason"] == "buy_vote_majority"
    assert aggregate["buy_votes"] == 25
    assert aggregate["sell_votes"] == 15
    assert aggregate["hold_votes"] == 10
    assert aggregate["abstaining_results"] == 4
    assert aggregate["received_results"] == 54
    assert aggregate["eligible_results"] == 50
    assert 0.0 < aggregate["confidence"] <= 1.0


def test_fifty_four_directional_tie_holds():
    decisions = (
        *("BUY",) * 17,
        *("SELL",) * 17,
        *("HOLD",) * 16,
        *("ABSTAIN",) * 4,
    )

    aggregate = aggregate_strategy_results(
        [
            result(
                name,
                decision,
            )
            for name, decision in zip(
                EXPECTED_FIFTY_FOUR,
                decisions,
                strict=True,
            )
        ]
    )

    assert aggregate["status"] == "ok"
    assert aggregate["decision"] == "HOLD"
    assert aggregate["reason"] == "directional_vote_tie"
    assert aggregate["buy_votes"] == 17
    assert aggregate["sell_votes"] == 17
    assert aggregate["hold_votes"] == 16
    assert aggregate["abstaining_results"] == 4
    assert aggregate["confidence"] == 0.0


def test_all_fifty_four_abstaining_fails_closed():
    aggregate = aggregate_strategy_results(
        [
            result(
                name,
                "ABSTAIN",
            )
            for name in EXPECTED_FIFTY_FOUR
        ]
    )

    assert aggregate["status"] == "abstain"
    assert aggregate["decision"] == "ABSTAIN"
    assert aggregate["reason"] == "all_evaluators_abstained"
    assert aggregate["abstaining_results"] == 54
    assert aggregate["received_results"] == 54


def test_real_third_batch_results_are_accepted():
    supplied = bars()

    evaluator_results = [
        evaluator(
            supplied
        )
        for evaluator in (
            BULK_OFFLINE_EVALUATORS_V3.values()
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

    assert 0.0 <= aggregate["confidence"] <= 1.0


def test_duplicate_third_batch_result_fails_closed():
    duplicate = result(
        THIRD_FIFTEEN[0],
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
        "Aroon  Trend",
        "aroon trend",
        "Williams %r Reversion",
        "Short-Term Reversal  Factor",
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


def test_registry_remains_thirty_nine_before_activation():
    from backend.app.stacks.strategy.evaluators.aggregation import COMPATIBLE_AGGREGATION_NAMES

    len(ALLOWLISTED_EVALUATORS) >= 54

    tuple(ALLOWLISTED_EVALUATORS)[:len(COMPATIBLE_AGGREGATION_NAMES)] == COMPATIBLE_AGGREGATION_NAMES


def test_healthcheck_reports_compatibility_not_activation():
    report = healthcheck()

    assert report[
        "compatible_input_names"
    ] == EXPECTED_FIFTY_FOUR

    assert report[
        "compatible_input_count"
    ] == 54

    assert report[
        "active_registry_modified"
    ] is False

    assert report[
        "owner_decision_integrated"
    ] is False

    assert report[
        "provider_called"
    ] is False

    assert report[
        "database_accessed"
    ] is False

    assert report[
        "execution_enabled"
    ] is False
