from __future__ import annotations

import pytest

from backend.app.stacks.strategy_candidate_sandbox.adaptive_training_controller import (
    adaptive_controller_status,
    get_adaptive_controller,
    run_adaptive_training_controller,
)

from backend.app.stacks.strategy_candidate_sandbox.training_candidate_contract import (
    build_training_candidate_contract,
)


def assert_execution_zero(
    result: dict,
) -> None:
    for round_record in result[
        "rounds"
    ]:
        assert all(
            value == 0
            for value
            in round_record[
                "execution_counters"
            ].values()
        )


def test_controller_status_is_safe() -> None:
    status = (
        adaptive_controller_status()
    )

    assert status[
        "automatic_strategy_promotion"
    ] is False

    assert status[
        "paper_order_creation"
    ] is False

    assert status[
        "portfolio_mutation"
    ] is False

    assert status[
        "model_mutation"
    ] is False

    assert status[
        "broker_execution"
    ] is False

    assert status[
        "live_execution"
    ] is False


@pytest.mark.parametrize(
    "threshold",
    [-0.1, 1.1],
)
def test_threshold_is_bounded(
    threshold: float,
) -> None:
    with pytest.raises(
        ValueError
    ):
        run_adaptive_training_controller(
            confidence_threshold=(
                threshold
            ),
            maximum_rounds=1,
        )


@pytest.mark.parametrize(
    "maximum_rounds",
    [0, 11],
)
def test_round_count_is_bounded(
    maximum_rounds: int,
) -> None:
    with pytest.raises(
        ValueError
    ):
        run_adaptive_training_controller(
            confidence_threshold=0.5,
            maximum_rounds=(
                maximum_rounds
            ),
        )


def test_controller_stops_at_immediate_threshold() -> None:
    result = (
        run_adaptive_training_controller(
            confidence_threshold=0.0,
            maximum_rounds=3,
            duration_seconds_per_round=1,
            lookback_rows=120,
            row_offset=0,
            requested_by=(
                "pytest-immediate-stop"
            ),
        )
    )

    assert result[
        "status"
    ] == "completed"

    assert result[
        "stop_reason"
    ] == "confidence_threshold_met"

    assert result[
        "rounds_completed"
    ] == 1

    assert len(
        result["rounds"]
    ) == 1

    assert result[
        "rounds"
    ][0][
        "ledger_persisted"
    ] is True

    assert_execution_zero(
        result
    )


def test_controller_reaches_maximum_rounds() -> None:
    candidate = (
        build_training_candidate_contract(
            short_lookback_rows=5,
            long_lookback_rows=20,
            minimum_signal_strength=0.01,
            created_from="qualification",
        )
        .to_dict()
    )

    result = (
        run_adaptive_training_controller(
            confidence_threshold=1.0,
            maximum_rounds=2,
            duration_seconds_per_round=1,
            initial_candidate=candidate,
            lookback_rows=120,
            row_offset=0,
            requested_by=(
                "pytest-maximum-rounds"
            ),
        )
    )

    assert result[
        "status"
    ] == "completed"

    assert result[
        "stop_reason"
    ] == "maximum_rounds_reached"

    assert result[
        "rounds_completed"
    ] == 2

    assert len(
        result["rounds"]
    ) == 2

    first = result[
        "rounds"
    ][0]

    second = result[
        "rounds"
    ][1]

    assert (
        first["candidate_id"]
        != second["candidate_id"]
    )

    assert (
        first["training_window_id"]
        != second["training_window_id"]
    )

    assert (
        first["training_window"][
            "round_number"
        ]
        == 1
    )

    assert (
        second["training_window"][
            "round_number"
        ]
        == 2
    )

    assert all(
        round_record[
            "ledger_persisted"
        ]
        is True
        for round_record
        in result["rounds"]
    )

    assert_execution_zero(
        result
    )

    loaded = get_adaptive_controller(
        result["controller_id"]
    )

    assert loaded == result
