from __future__ import annotations

from copy import deepcopy
import time

from backend.app.stacks.strategy_candidate_sandbox.training_candidate_contract import (
    build_training_candidate_contract,
)
from backend.app.stacks.strategy_candidate_sandbox.training_window_contract import (
    build_training_window_contract,
)
from backend.app.stacks.strategy_candidate_sandbox.bounded_training_confidence_pipeline import (
    build_bounded_training_confidence_summary,
)
from backend.app.stacks.strategy_candidate_sandbox.persistent_learning_ledger import (
    validate_sanitized_contribution,
)
from backend.app.stacks.strategy_candidate_sandbox.L4_runtime_orchestration.bounded_training_runtime import (
    discover_canadian_datasets,
    get_training_session,
    start_bounded_training_session,
)


def wait_for_terminal(
    run_id: str,
    timeout: float = 120.0,
) -> dict:
    deadline = (
        time.monotonic()
        + timeout
    )

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


def legacy_contribution() -> dict:
    return {
        "contribution_id":
            "contribution_legacy_v32",

        "source_scope":
            "system",

        "universe":
            "canada",

        "completed":
            True,

        "duration_seconds":
            1,

        "elapsed_seconds":
            1.0,

        "symbols_evaluated":
            1,

        "rows_evaluated":
            2,

        "cycles":
            1,

        "signal_totals": {
            "BUY_SIGNAL": 1,
            "SELL_SIGNAL": 0,
            "HOLD": 1,
        },

        "safety": {
            "customer_identity_included":
                False,

            "session_identity_included":
                False,

            "portfolio_data_included":
                False,

            "order_data_included":
                False,

            "chat_content_included":
                False,

            "authentication_data_included":
                False,

            "broker_execution":
                False,

            "live_execution":
                False,
        },
    }


def test_legacy_contribution_still_validates() -> None:
    assert (
        validate_sanitized_contribution(
            legacy_contribution()
        )
        is True
    )


def test_partial_provenance_is_rejected() -> None:
    contribution = (
        legacy_contribution()
    )

    contribution[
        "candidate_id"
    ] = (
        "training_candidate_"
        + "0" * 24
    )

    assert (
        validate_sanitized_contribution(
            contribution
        )
        is False
    )


def test_confidence_summary_contains_complete_provenance() -> None:
    candidate = (
        build_training_candidate_contract(
            short_lookback_rows=5,
            long_lookback_rows=20,
            minimum_signal_strength=0.01,
            created_from="qualification",
        ).to_dict()
    )

    window = (
        build_training_window_contract(
            lookback_rows=120,
            row_offset=10,
            round_number=2,
            maximum_rounds=4,
        ).to_dict()
    )

    summary = (
        build_bounded_training_confidence_summary(
            run_id="confidence-v32",
            datasets=(
                discover_canadian_datasets()
            ),
            training_candidate=candidate,
            training_window=window,
        )
    )

    assert summary[
        "training_candidate"
    ] == candidate

    assert summary[
        "candidate_id"
    ] == candidate[
        "candidate_id"
    ]

    assert summary[
        "training_window"
    ] == window

    assert summary[
        "training_window_id"
    ] == window[
        "training_window_id"
    ]


def test_provenance_tampering_is_rejected() -> None:
    candidate = (
        build_training_candidate_contract(
            created_from="qualification",
        ).to_dict()
    )

    window = (
        build_training_window_contract(
            lookback_rows=120,
        ).to_dict()
    )

    contribution = (
        legacy_contribution()
    )

    contribution.update(
        {
            "candidate_id":
                candidate["candidate_id"],

            "training_candidate":
                candidate,

            "training_window_id":
                window[
                    "training_window_id"
                ],

            "training_window":
                window,

            "window_start":
                window["window_start"],

            "window_end":
                window["window_end"],

            "lookback_rows":
                window["lookback_rows"],

            "row_offset":
                window["row_offset"],

            "round_number":
                window["round_number"],

            "maximum_rounds":
                window["maximum_rounds"],
        }
    )

    assert (
        validate_sanitized_contribution(
            contribution
        )
        is True
    )

    tampered = deepcopy(
        contribution
    )

    tampered[
        "row_offset"
    ] = 999

    assert (
        validate_sanitized_contribution(
            tampered
        )
        is False
    )


def test_runtime_persists_exact_candidate_and_window() -> None:
    candidate = (
        build_training_candidate_contract(
            short_lookback_rows=5,
            long_lookback_rows=20,
            minimum_signal_strength=0.01,
            created_from="qualification",
        ).to_dict()
    )

    started = (
        start_bounded_training_session(
            duration_seconds=1,
            universe="canada",
            requested_by=(
                "confidence-ledger-v32"
            ),
            source="pytest",
            scope="system",
            requested_by_role="developer",
            training_candidate=candidate,
            lookback_rows=120,
            row_offset=10,
            round_number=2,
            maximum_rounds=4,
        )
    )

    completed = wait_for_terminal(
        started["run_id"]
    )

    assert completed[
        "status"
    ] == "completed"

    contribution = completed[
        "sanitized_learning_contribution"
    ]

    assert contribution[
        "training_candidate"
    ] == candidate

    assert contribution[
        "candidate_id"
    ] == candidate[
        "candidate_id"
    ]

    assert contribution[
        "training_window"
    ] == started[
        "training_window"
    ]

    assert contribution[
        "training_window_id"
    ] == started[
        "training_window_id"
    ]

    assert completed[
        "confidence_pipeline_status"
    ] == "completed"

    assert completed[
        "learning_ledger_status"
    ] in {
        "persisted",
        "already_persisted",
    }

    assert (
        validate_sanitized_contribution(
            contribution
        )
        is True
    )

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
