import pytest

from backend.app.stacks.strategy.evaluators.aggregation import (
    QUALIFIED_AGGREGATION_NAMES,
    aggregate_strategy_results,
    healthcheck,
)


SMA = "Simple Moving Average Crossover"
BREAKOUT = "Bollinger Band Breakout"
MEAN_REVERSION = "Bollinger Band Mean Reversion"
RSI_OVERBOUGHT = "RSI Overbought Mean Reversion"
RSI_OVERSOLD = "RSI Oversold Mean Reversion"


def result(
    strategy_name,
    decision,
    confidence=0.5,
):
    normalized = decision.upper()

    return {
        "strategy_name": strategy_name,
        "evaluator_id": (
            strategy_name
            .lower()
            .replace(
                " ",
                "_",
            )
            +
            "_v1"
        ),
        "status": (
            "abstain"
            if normalized == "ABSTAIN"
            else "ok"
        ),
        "decision": normalized,
        "signal": normalized,
        "confidence": (
            0.0
            if normalized == "ABSTAIN"
            else confidence
        ),
        "reason": "test_fixture",
    }


def test_exact_five_qualified_input_names():
    assert QUALIFIED_AGGREGATION_NAMES == (
        SMA,
        BREAKOUT,
        MEAN_REVERSION,
        RSI_OVERBOUGHT,
        RSI_OVERSOLD,
    )


def test_single_buy_is_preserved():
    aggregated = aggregate_strategy_results(
        [
            result(
                SMA,
                "BUY",
                0.8,
            )
        ]
    )

    assert aggregated["status"] == "ok"
    assert aggregated["decision"] == "BUY"
    assert aggregated["buy_votes"] == 1
    assert aggregated["sell_votes"] == 0
    assert aggregated["confidence"] == pytest.approx(
        0.8
    )


def test_single_sell_is_preserved():
    aggregated = aggregate_strategy_results(
        [
            result(
                SMA,
                "SELL",
                0.6,
            )
        ]
    )

    assert aggregated["decision"] == "SELL"
    assert aggregated["confidence"] == pytest.approx(
        0.6
    )


def test_single_hold_is_preserved():
    aggregated = aggregate_strategy_results(
        [
            result(
                SMA,
                "HOLD",
                0.4,
            )
        ]
    )

    assert aggregated["decision"] == "HOLD"
    assert aggregated["reason"] == "no_directional_vote"
    assert aggregated["confidence"] == 0.0


def test_buy_majority_wins():
    aggregated = aggregate_strategy_results(
        [
            result(
                SMA,
                "BUY",
                0.8,
            ),
            result(
                BREAKOUT,
                "BUY",
                0.6,
            ),
            result(
                MEAN_REVERSION,
                "SELL",
                0.9,
            ),
        ]
    )

    assert aggregated["decision"] == "BUY"
    assert aggregated["reason"] == "buy_vote_majority"
    assert aggregated["buy_votes"] == 2
    assert aggregated["sell_votes"] == 1
    assert aggregated["net_vote"] == 1

    expected = (
        0.7
        *
        (
            2.0 / 3.0
        )
    )

    assert aggregated["confidence"] == pytest.approx(
        expected
    )


def test_sell_majority_wins():
    aggregated = aggregate_strategy_results(
        [
            result(
                SMA,
                "SELL",
                0.7,
            ),
            result(
                BREAKOUT,
                "BUY",
                0.5,
            ),
            result(
                RSI_OVERBOUGHT,
                "SELL",
                0.9,
            ),
        ]
    )

    assert aggregated["decision"] == "SELL"
    assert aggregated["sell_votes"] == 2
    assert aggregated["buy_votes"] == 1


def test_directional_tie_holds():
    aggregated = aggregate_strategy_results(
        [
            result(
                SMA,
                "BUY",
                0.9,
            ),
            result(
                BREAKOUT,
                "SELL",
                0.9,
            ),
        ]
    )

    assert aggregated["decision"] == "HOLD"
    assert aggregated["reason"] == "directional_vote_tie"
    assert aggregated["confidence"] == 0.0


def test_hold_does_not_break_directional_tie():
    aggregated = aggregate_strategy_results(
        [
            result(
                SMA,
                "BUY",
            ),
            result(
                BREAKOUT,
                "SELL",
            ),
            result(
                MEAN_REVERSION,
                "HOLD",
            ),
        ]
    )

    assert aggregated["decision"] == "HOLD"
    assert aggregated["buy_votes"] == 1
    assert aggregated["sell_votes"] == 1
    assert aggregated["hold_votes"] == 1


def test_hold_reduces_directional_participation_confidence():
    aggregated = aggregate_strategy_results(
        [
            result(
                SMA,
                "BUY",
                0.9,
            ),
            result(
                BREAKOUT,
                "HOLD",
                0.9,
            ),
        ]
    )

    assert aggregated["decision"] == "BUY"
    assert aggregated["participation_ratio"] == 0.5
    assert aggregated["confidence"] == pytest.approx(
        0.45
    )


def test_abstention_is_excluded():
    aggregated = aggregate_strategy_results(
        [
            result(
                SMA,
                "BUY",
                0.7,
            ),
            result(
                BREAKOUT,
                "ABSTAIN",
            ),
        ]
    )

    assert aggregated["decision"] == "BUY"
    assert aggregated["eligible_results"] == 1
    assert aggregated["abstaining_results"] == 1
    assert aggregated["confidence"] == pytest.approx(
        0.7
    )


def test_all_abstaining_produces_abstain():
    aggregated = aggregate_strategy_results(
        [
            result(
                SMA,
                "ABSTAIN",
            ),
            result(
                BREAKOUT,
                "ABSTAIN",
            ),
        ]
    )

    assert aggregated["status"] == "abstain"
    assert aggregated["decision"] == "ABSTAIN"
    assert aggregated["reason"] == "all_evaluators_abstained"
    assert aggregated["confidence"] == 0.0
    assert aggregated["abstaining_results"] == 2


def test_empty_results_abstain():
    aggregated = aggregate_strategy_results(
        []
    )

    assert aggregated["status"] == "abstain"
    assert aggregated["decision"] == "ABSTAIN"
    assert aggregated["reason"] == "no_evaluator_results"


def test_duplicate_strategy_results_fail_closed():
    aggregated = aggregate_strategy_results(
        [
            result(
                SMA,
                "BUY",
            ),
            result(
                SMA,
                "SELL",
            ),
        ]
    )

    assert aggregated["status"] == "abstain"
    assert aggregated["decision"] == "ABSTAIN"
    assert aggregated["reason"] == "duplicate_strategy_results"


def test_unknown_strategy_fails_closed():
    aggregated = aggregate_strategy_results(
        [
            result(
                "Unknown Strategy",
                "BUY",
            )
        ]
    )

    assert aggregated["status"] == "abstain"
    assert aggregated["reason"] == "invalid_evaluator_results"
    assert "unqualified strategy" in aggregated["error"]


@pytest.mark.parametrize(
    "bad_results",
    [
        None,
        "not-results",
        [
            None
        ],
        [
            {
                "strategy_name": SMA,
                "decision": "INVALID",
                "confidence": 0.5,
            }
        ],
        [
            {
                "strategy_name": SMA,
                "decision": "BUY",
                "confidence": float(
                    "nan"
                ),
            }
        ],
        [
            {
                "strategy_name": SMA,
                "decision": "BUY",
                "confidence": 1.1,
            }
        ],
        [
            {
                "strategy_name": SMA,
                "decision": "BUY",
                "confidence": -0.1,
            }
        ],
    ],
)
def test_malformed_results_fail_closed(
    bad_results,
):
    aggregated = aggregate_strategy_results(
        bad_results
    )

    assert aggregated["status"] == "abstain"
    assert aggregated["decision"] == "ABSTAIN"
    assert aggregated["confidence"] == 0.0


def test_inconsistent_status_and_decision_fail_closed():
    malformed = result(
        SMA,
        "BUY",
    )

    malformed[
        "status"
    ] = "abstain"

    aggregated = aggregate_strategy_results(
        [
            malformed
        ]
    )

    assert aggregated["status"] == "abstain"
    assert aggregated["reason"] == "invalid_evaluator_results"


def test_abstention_with_nonzero_confidence_fails_closed():
    malformed = result(
        SMA,
        "ABSTAIN",
    )

    malformed[
        "confidence"
    ] = 0.5

    aggregated = aggregate_strategy_results(
        [
            malformed
        ]
    )

    assert aggregated["status"] == "abstain"
    assert aggregated["reason"] == "invalid_evaluator_results"


def test_input_order_does_not_change_decision_or_confidence():
    forward = [
        result(
            SMA,
            "BUY",
            0.8,
        ),
        result(
            BREAKOUT,
            "BUY",
            0.6,
        ),
        result(
            MEAN_REVERSION,
            "SELL",
            0.9,
        ),
        result(
            RSI_OVERBOUGHT,
            "HOLD",
            0.2,
        ),
    ]

    reverse = list(
        reversed(
            forward
        )
    )

    first = aggregate_strategy_results(
        forward
    )

    second = aggregate_strategy_results(
        reverse
    )

    assert first["decision"] == second["decision"]
    assert first["confidence"] == pytest.approx(
        second["confidence"]
    )
    assert first["buy_votes"] == second["buy_votes"]
    assert first["sell_votes"] == second["sell_votes"]
    assert first["hold_votes"] == second["hold_votes"]


def test_repeated_aggregation_is_deterministic():
    inputs = [
        result(
            SMA,
            "SELL",
            0.4,
        ),
        result(
            BREAKOUT,
            "SELL",
            0.8,
        ),
        result(
            RSI_OVERSOLD,
            "HOLD",
            0.3,
        ),
    ]

    assert (
        aggregate_strategy_results(
            inputs
        )
        ==
        aggregate_strategy_results(
            inputs
        )
    )


def test_healthcheck_does_not_claim_activation():
    status = healthcheck()

    assert status["healthy"] is True
    assert status["aggregation_policy"] == (
        "equal_directional_vote_majority"
    )
    assert status["abstentions_excluded"] is True
    assert status["duplicates_fail_closed"] is True
    assert status["unknown_strategies_fail_closed"] is True
    assert status["active_registry_modified"] is False
    assert status["owner_decision_integrated"] is False
    assert status["provider_called"] is False
    assert status["database_accessed"] is False
    assert status["execution_enabled"] is False


def test_native_sma_abstention_is_accepted_and_canonicalized():
    from backend.app.stacks.strategy.evaluators.sma_crossover import (
        evaluate_sma_crossover,
    )

    sma_result = evaluate_sma_crossover(
        [
            {
                "close": 100.0,
            }
        ] * 20
    )

    assert sma_result[
        "status"
    ] == "abstained"

    assert sma_result[
        "decision"
    ] == "ABSTAIN"

    assert sma_result[
        "signal"
    ] == "hold"

    assert sma_result[
        "confidence"
    ] == 0.0

    aggregated = aggregate_strategy_results(
        [
            sma_result
        ]
    )

    assert aggregated[
        "status"
    ] == "abstain"

    assert aggregated[
        "decision"
    ] == "ABSTAIN"

    assert aggregated[
        "reason"
    ] == "all_evaluators_abstained"

    assert aggregated[
        "abstaining_results"
    ] == 1

    assert aggregated[
        "strategy_results"
    ][0][
        "status"
    ] == "abstain"


def test_native_sma_abstention_is_excluded_from_family_vote():
    from backend.app.stacks.strategy.evaluators.sma_crossover import (
        evaluate_sma_crossover,
    )

    sma_result = evaluate_sma_crossover(
        [
            {
                "close": 100.0,
            }
        ] * 20
    )

    family_result = result(
        BREAKOUT,
        "BUY",
        0.75,
    )

    aggregated = aggregate_strategy_results(
        [
            sma_result,
            family_result,
        ]
    )

    assert aggregated[
        "status"
    ] == "ok"

    assert aggregated[
        "decision"
    ] == "BUY"

    assert aggregated[
        "confidence"
    ] == pytest.approx(
        0.75
    )

    assert aggregated[
        "eligible_results"
    ] == 1

    assert aggregated[
        "abstaining_results"
    ] == 1

    assert aggregated[
        "abstaining_strategies"
    ] == [
        SMA
    ]


def test_abstained_status_with_non_abstain_decision_still_fails_closed():
    malformed = {
        "strategy_name": SMA,
        "evaluator_id": "simple_moving_average_crossover_v1",
        "status": "abstained",
        "decision": "HOLD",
        "signal": "hold",
        "confidence": 0.0,
        "reason": "malformed_fixture",
    }

    aggregated = aggregate_strategy_results(
        [
            malformed
        ]
    )

    assert aggregated[
        "status"
    ] == "abstain"

    assert aggregated[
        "decision"
    ] == "ABSTAIN"

    assert aggregated[
        "reason"
    ] == "invalid_evaluator_results"


def test_abstained_status_with_nonzero_confidence_still_fails_closed():
    malformed = {
        "strategy_name": SMA,
        "evaluator_id": "simple_moving_average_crossover_v1",
        "status": "abstained",
        "decision": "ABSTAIN",
        "signal": "hold",
        "confidence": 0.1,
        "reason": "malformed_fixture",
    }

    aggregated = aggregate_strategy_results(
        [
            malformed
        ]
    )

    assert aggregated[
        "status"
    ] == "abstain"

    assert aggregated[
        "decision"
    ] == "ABSTAIN"

    assert aggregated[
        "reason"
    ] == "invalid_evaluator_results"
