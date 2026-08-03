from __future__ import annotations

from typing import Any
import time

from backend.app.stacks.strategy_candidate_sandbox.L4_runtime_orchestration.bounded_training_runtime import (
    discover_canadian_datasets,
    get_training_session,
    start_bounded_training_session,
)

from backend.app.stacks.strategy_candidate_sandbox.bounded_training_confidence_pipeline import (
    build_bounded_training_confidence_summary,
)

from backend.app.stacks.strategy_candidate_sandbox.persistent_learning_ledger import (
    get_learning_contribution,
    validate_sanitized_contribution,
)


FORBIDDEN_KEYS = {
    "owner_user_id",
    "owner_session_id",
    "user_id",
    "session_id",
    "email",
    "password",
    "prompt",
    "raw_prompt",
    "portfolio",
    "positions",
    "holdings",
    "orders",
    "access_token",
    "refresh_token",
    "credential",
    "broker",
    "broker_token",
    "requested_by",
    "requested_by_role",
}


def inspect_keys(
    value: Any,
) -> set[str]:
    found: set[str] = set()

    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(
                key
            ).strip().lower()

            if normalized in FORBIDDEN_KEYS:
                found.add(
                    normalized
                )

            found.update(
                inspect_keys(child)
            )

    elif isinstance(value, list):
        for child in value:
            found.update(
                inspect_keys(child)
            )

    return found


def test_direct_confidence_pipeline_profiles_all_symbols() -> None:
    summary = (
        build_bounded_training_confidence_summary(
            run_id="confidence_direct_test",
            datasets=discover_canadian_datasets(),
        )
    )

    assert (
        summary[
            "valid_learning_artifacts"
        ]
        > 0
    )

    assert (
        summary[
            "learning_observations"
        ]
        > 0
    )

    assert (
        summary[
            "symbols_with_valid_confidence"
        ]
        >= 55
    )

    assert (
        len(
            summary[
                "symbol_confidence"
            ]
        )
        >= 55
    )

    assert (
        0.0
        <= summary[
            "average_confidence"
        ]
        <= 1.0
    )

    assert (
        inspect_keys(summary)
        == set()
    )


def test_ledger_accepts_confidence_contract() -> None:
    summary = (
        build_bounded_training_confidence_summary(
            run_id="confidence_contract_test",
            datasets=discover_canadian_datasets(),
        )
    )

    contribution = {
        "contribution_id":
            "contribution_confidence_contract_test",

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
            55,

        "rows_evaluated":
            100,

        "cycles":
            2,

        "signal_totals": {
            "BUY_SIGNAL": 40,
            "SELL_SIGNAL": 30,
            "HOLD": 30,
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

        **summary,
    }

    assert (
        validate_sanitized_contribution(
            contribution
        )
        is True
    )


def test_bounded_run_persists_confidence_summary() -> None:
    started = start_bounded_training_session(
        duration_seconds=1,
        universe="canada",
        requested_by="confidence-runtime-test",
        source="test",
        scope="system",
        requested_by_role="developer",
    )

    run_id = started["run_id"]
    deadline = time.monotonic() + 60
    record = None

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
            and record.get(
                "learning_ledger_status"
            )
            in {
                "persisted",
                "already_persisted",
                "failed",
            }
        ):
            break

        time.sleep(0.1)

    assert record is not None
    assert record["status"] == "completed"

    assert (
        record[
            "learning_ledger_status"
        ]
        in {
            "persisted",
            "already_persisted",
        }
    )

    assert (
        record[
            "valid_learning_artifacts"
        ]
        > 0
    )

    assert (
        record[
            "learning_observations"
        ]
        > 0
    )

    assert (
        record[
            "symbols_with_valid_confidence"
        ]
        >= 55
    )

    assert (
        0.0
        <= record[
            "average_confidence"
        ]
        <= 1.0
    )

    stored = get_learning_contribution(
        record[
            "learning_contribution_id"
        ]
    )

    assert stored is not None

    contribution = stored[
        "contribution"
    ]

    assert (
        len(
            contribution[
                "symbol_confidence"
            ]
        )
        >= 55
    )

    assert (
        inspect_keys(stored)
        == set()
    )

    assert record["model_updates"] == 0
    assert record["database_rows_written"] == 0
    assert record["strategy_promotions"] == 0
    assert record["paper_orders_created"] == 0
    assert record["portfolio_mutations"] == 0
    assert record["broker_requests"] == 0
    assert record["live_orders"] == 0
