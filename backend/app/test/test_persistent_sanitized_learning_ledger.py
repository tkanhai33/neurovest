from __future__ import annotations

from pathlib import Path
from uuid import uuid4
import json
import time

import pytest

from backend.app.stacks.strategy_candidate_sandbox.L4_runtime_orchestration.bounded_training_runtime import (
    get_training_session,
    start_bounded_training_session,
)

from backend.app.stacks.strategy_candidate_sandbox.persistent_learning_ledger import (
    get_learning_contribution,
    learning_ledger_status,
    list_learning_contributions,
    persist_sanitized_learning_contribution,
    validate_sanitized_contribution,
)


FORBIDDEN_TEXT = (
    "owner_user_id",
    "owner_session_id",
    "user_id",
    "session_id",
    "email",
    "password",
    "prompt",
    "portfolio",
    "positions",
    "holdings",
    "orders",
    "access_token",
    "refresh_token",
    "credential",
    "broker_token",
    "requested_by",
    "requested_by_role",
)



def forbidden_keys_present(
    value: object,
) -> set[str]:
    found: set[str] = set()

    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(
                key
            ).strip().lower()

            if normalized in FORBIDDEN_TEXT:
                found.add(
                    normalized
                )

            found.update(
                forbidden_keys_present(
                    child
                )
            )

    elif isinstance(value, list):
        for child in value:
            found.update(
                forbidden_keys_present(
                    child
                )
            )

    return found


def contribution(
    *,
    contribution_id: str | None = None,
) -> dict:
    return {
        "contribution_id":
            contribution_id
            or (
                "contribution_"
                + uuid4().hex
            ),

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
            "BUY_SIGNAL": 30,
            "SELL_SIGNAL": 20,
            "HOLD": 50,
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


def test_valid_sanitized_contribution_is_accepted() -> None:
    assert (
        validate_sanitized_contribution(
            contribution()
        )
        is True
    )


@pytest.mark.parametrize(
    "forbidden_key",
    FORBIDDEN_TEXT,
)
def test_forbidden_identity_and_customer_fields_are_rejected(
    forbidden_key: str,
) -> None:
    payload = contribution()

    payload[
        forbidden_key
    ] = "must-not-persist"

    assert (
        validate_sanitized_contribution(
            payload
        )
        is False
    )


def test_nested_forbidden_fields_are_rejected() -> None:
    payload = contribution()

    payload["safety"][
        "metadata"
    ] = {
        "owner_user_id":
            "must-not-persist",
    }

    assert (
        validate_sanitized_contribution(
            payload
        )
        is False
    )


def test_contribution_is_written_and_read_back() -> None:
    payload = contribution()

    result = (
        persist_sanitized_learning_contribution(
            payload
        )
    )

    assert result["status"] in {
        "persisted",
        "already_persisted",
    }

    stored = get_learning_contribution(
        payload[
            "contribution_id"
        ]
    )

    assert stored is not None

    assert (
        stored[
            "contribution"
        ]
        == payload
    )

    assert (
        forbidden_keys_present(
            stored
        )
        == set()
    )


def test_ledger_is_idempotent_by_contribution_id() -> None:
    payload = contribution()

    first = (
        persist_sanitized_learning_contribution(
            payload
        )
    )

    second = (
        persist_sanitized_learning_contribution(
            payload
        )
    )

    assert first["status"] in {
        "persisted",
        "already_persisted",
    }

    assert (
        second["status"]
        == "already_persisted"
    )


def test_ledger_can_list_previous_contributions() -> None:
    payload = contribution()

    persist_sanitized_learning_contribution(
        payload
    )

    records = list_learning_contributions(
        limit=1000
    )

    ids = {
        str(
            item.get(
                "contribution",
                {},
            ).get(
                "contribution_id",
                "",
            )
        )
        for item in records
    }

    assert (
        payload[
            "contribution_id"
        ]
        in ids
    )


def test_ledger_status_remains_fail_closed() -> None:
    status = learning_ledger_status()

    assert status["ledger_enabled"] is True
    assert status["append_only"] is True

    assert (
        status[
            "database_writes_enabled"
        ]
        is False
    )

    assert (
        status[
            "strategy_promotion_enabled"
        ]
        is False
    )

    assert (
        status[
            "broker_execution_enabled"
        ]
        is False
    )

    assert (
        status[
            "live_execution_enabled"
        ]
        is False
    )

    assert (
        status[
            "customer_identity_allowed"
        ]
        is False
    )

    assert (
        status[
            "session_identity_allowed"
        ]
        is False
    )


def test_completed_bounded_run_persists_learning_contribution() -> None:
    started = start_bounded_training_session(
        duration_seconds=1,
        universe="canada",
        requested_by=(
            "persistent-ledger-pytest"
        ),
        source="test",
        scope="system",
        requested_by_role="developer",
    )

    run_id = started["run_id"]
    deadline = time.monotonic() + 20
    record = None

    while time.monotonic() < deadline:
        record = get_training_session(
            run_id
        )

        if (
            record
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

        time.sleep(0.05)

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
            "learning_artifacts_written"
        ]
        in {
            0,
            1,
        }
    )

    assert (
        record[
            "learning_updates"
        ]
        in {
            0,
            1,
        }
    )

    assert record["model_updates"] == 0

    contribution_id = record[
        "learning_contribution_id"
    ]

    stored = get_learning_contribution(
        contribution_id
    )

    assert stored is not None

    assert (
        forbidden_keys_present(
            stored
        )
        == set()
    )

    assert record["database_rows_written"] == 0
    assert record["strategy_promotions"] == 0
    assert record["paper_orders_created"] == 0
    assert record["portfolio_mutations"] == 0
    assert record["broker_requests"] == 0
    assert record["live_orders"] == 0
