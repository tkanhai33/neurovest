from __future__ import annotations

from typing import Any
import time

from backend.app.stacks.strategy_candidate_sandbox.L4_runtime_orchestration.bounded_training_runtime import (
    get_training_session,
    start_bounded_training_session,
)

from backend.app.stacks.strategy_candidate_sandbox.training_confidence_baseline import (
    build_confidence_baseline_comparison,
)


def _wait(
    run_id: str,
) -> dict[str, Any]:
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
        "Training run did not finish."
    )


def test_first_contribution_has_no_required_baseline() -> None:
    current = {
        "contribution_id":
            "baseline-unit-current",

        "universe":
            "canada",

        "average_confidence":
            0.4,

        "symbol_confidence": [
            {
                "symbol": "RY.TO",
                "average_confidence": 0.4,
            },
        ],
    }

    result = (
        build_confidence_baseline_comparison(
            current_contribution=current,
        )
    )

    assert (
        result[
            "current_average_confidence"
        ]
        == 0.4
    )

    assert isinstance(
        result[
            "confidence_baseline_available"
        ],
        bool,
    )


def test_two_training_runs_create_baseline_comparison() -> None:
    first = start_bounded_training_session(
        duration_seconds=1,
        universe="canada",
        requested_by="baseline-first",
        source="pytest",
        scope="system",
        requested_by_role="developer",
    )

    first_record = _wait(
        first["run_id"]
    )

    assert (
        first_record["status"]
        == "completed"
    )

    second = start_bounded_training_session(
        duration_seconds=1,
        universe="canada",
        requested_by="baseline-second",
        source="pytest",
        scope="system",
        requested_by_role="developer",
    )

    second_record = _wait(
        second["run_id"]
    )

    assert (
        second_record["status"]
        == "completed"
    )

    assert (
        second_record[
            "confidence_pipeline_status"
        ]
        == "completed"
    )

    assert (
        second_record[
            "learning_ledger_status"
        ]
        in {
            "persisted",
            "already_persisted",
        }
    )

    assert (
        second_record[
            "confidence_baseline_available"
        ]
        is True
    )

    assert (
        second_record[
            "baseline_contribution_id"
        ]
        == first_record[
            "learning_contribution_id"
        ]
    )

    assert (
        second_record[
            "symbols_compared"
        ]
        >= 55
    )

    assert (
        second_record[
            "symbols_improved"
        ]
        + second_record[
            "symbols_unchanged"
        ]
        + second_record[
            "symbols_declined"
        ]
        == second_record[
            "symbols_compared"
        ]
    )

    assert (
        -1.0
        <= float(
            second_record[
                "average_confidence_delta"
            ]
        )
        <= 1.0
    )

    for key in (
        "paper_orders_created",
        "portfolio_mutations",
        "database_rows_written",
        "strategy_promotions",
        "broker_requests",
        "live_orders",
        "model_updates",
    ):
        assert second_record[key] == 0
