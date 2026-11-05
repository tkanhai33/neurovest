from __future__ import annotations

import time

from backend.app.stacks.strategy_candidate_sandbox.training_candidate_contract import (
    build_training_candidate_contract,
)
from backend.app.stacks.strategy_candidate_sandbox.training_window_contract import (
    apply_training_window,
    build_close_prefix_sums,
    build_training_window_contract,
    candidate_decision_from_prefix,
    validate_training_window_contract,
)
from backend.app.stacks.strategy_candidate_sandbox.L4_runtime_orchestration.bounded_training_runtime import (
    get_training_session,
    start_bounded_training_session,
)


def wait_for_terminal(
    run_id: str,
) -> dict:
    deadline = time.monotonic() + 120

    while time.monotonic() < deadline:
        record = get_training_session(
            run_id
        )

        if (
            isinstance(record, dict)
            and record.get("status")
            in {
                "completed",
                "failed",
            }
        ):
            return record

        time.sleep(0.02)

    raise AssertionError(
        "training run did not complete"
    )


def test_window_contract_is_deterministic() -> None:
    first = build_training_window_contract(
        lookback_rows=120,
        row_offset=10,
        round_number=2,
        maximum_rounds=4,
    )

    second = build_training_window_contract(
        lookback_rows=120,
        row_offset=10,
        round_number=2,
        maximum_rounds=4,
    )

    assert first == second

    assert validate_training_window_contract(
        first.to_dict()
    )


def test_window_application_is_exact() -> None:
    window = build_training_window_contract(
        window_start="2024-01-02",
        window_end="2024-01-05",
        lookback_rows=2,
        row_offset=1,
    )

    assert apply_training_window(
        [1, 2, 3, 4, 5],
        timestamps=[
            "2024-01-01",
            "2024-01-02",
            "2024-01-03",
            "2024-01-04",
            "2024-01-05",
        ],
        window=window.to_dict(),
    ) == [3, 4]


def test_prefix_decision_uses_candidate() -> None:
    closes = [
        100.0,
        100.0,
        100.0,
        101.0,
        102.0,
        103.0,
        104.0,
        105.0,
    ]

    prefix = build_close_prefix_sums(
        closes
    )

    candidate = (
        build_training_candidate_contract(
            short_lookback_rows=2,
            long_lookback_rows=5,
            minimum_signal_strength=0.0,
            created_from="qualification",
            strategy_name='Qualification Test Moving Average Crossover',
        ).to_dict()
    )

    assert candidate_decision_from_prefix(
        closes=closes,
        prefix_sums=prefix,
        index=7,
        candidate=candidate,
    ) == "BUY_SIGNAL"


def test_runtime_records_candidate_and_window() -> None:
    candidate = (
        build_training_candidate_contract(
            short_lookback_rows=5,
            long_lookback_rows=20,
            minimum_signal_strength=0.01,
            created_from="qualification",
            strategy_name='Qualification Test Moving Average Crossover',
        ).to_dict()
    )

    started = start_bounded_training_session(
        duration_seconds=1,
        universe="canada",
        requested_by="runtime-v31-proof",
        source="pytest",
        scope="system",
        requested_by_role="developer",
        training_candidate=candidate,
        lookback_rows=120,
        row_offset=10,
        round_number=2,
        maximum_rounds=4,
    )

    completed = wait_for_terminal(
        started["run_id"]
    )

    assert completed["status"] == "completed"

    assert (
        completed["candidate_id"]
        == candidate["candidate_id"]
    )

    assert (
        completed["training_candidate"]
        == candidate
    )

    assert (
        completed["training_window_id"]
        == started["training_window_id"]
    )

    assert (
        completed["training_window"]
        == started["training_window"]
    )

    assert completed["lookback_rows"] == 120
    assert completed["row_offset"] == 10
    assert completed["round_number"] == 2
    assert completed["maximum_rounds"] == 4

    assert all(
        completed.get(key) == 0
        for key in (
            "paper_orders_created",
            "portfolio_mutations",
            "database_rows_written",
            "strategy_promotions",
            "broker_requests",
            "live_orders",
            "model_updates",
        )
    )
