from pathlib import Path
import time

from backend.app.stacks.strategy_candidate_sandbox.L4_runtime_orchestration.bounded_training_runtime import (
    get_training_session,
    get_training_session_for_owner,
    list_training_sessions_for_owner,
    start_bounded_training_session,
)


MAIN = Path(
    "backend/app/main.py"
)

SERVICE = Path(
    "backend/app/stacks/"
    "strategy_candidate_sandbox/"
    "L4_runtime_orchestration/"
    "bounded_training_runtime.py"
)


def wait_for_completion(
    run_id: str,
) -> dict:
    deadline = time.monotonic() + 120

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
        ):
            return record

        time.sleep(0.05)

    raise AssertionError(
        "Training run did not complete."
    )


def test_user_run_requires_user_and_session_owner() -> None:
    try:
        start_bounded_training_session(
            duration_seconds=1,
            scope="user",
            owner_user_id=None,
            owner_session_id=None,
        )
    except ValueError as error:
        assert "owner user ID" in str(error)
    else:
        raise AssertionError(
            "Ownerless user run was accepted."
        )


def test_system_run_rejects_customer_owner() -> None:
    try:
        start_bounded_training_session(
            duration_seconds=1,
            scope="system",
            owner_user_id="customer-1",
            owner_session_id="session-1",
        )
    except ValueError as error:
        assert "cannot have a customer owner" in str(error)
    else:
        raise AssertionError(
            "Customer-owned system run was accepted."
        )


def test_two_users_cannot_read_each_others_runs() -> None:
    record = start_bounded_training_session(
        duration_seconds=1,
        universe="canada",
        requested_by="user-a",
        source="pytest",
        scope="user",
        owner_user_id="user-a",
        owner_session_id="session-a",
        requested_by_role="user",
    )

    run_id = record["run_id"]

    assert (
        get_training_session_for_owner(
            run_id=run_id,
            owner_user_id="user-a",
            owner_session_id="session-a",
        )
        is not None
    )

    assert (
        get_training_session_for_owner(
            run_id=run_id,
            owner_user_id="user-b",
            owner_session_id="session-b",
        )
        is None
    )


def test_same_user_new_session_cannot_read_old_run() -> None:
    record = start_bounded_training_session(
        duration_seconds=1,
        universe="canada",
        requested_by="user-a",
        source="pytest",
        scope="user",
        owner_user_id="user-a",
        owner_session_id="session-original",
        requested_by_role="user",
    )

    assert (
        get_training_session_for_owner(
            run_id=record["run_id"],
            owner_user_id="user-a",
            owner_session_id="session-new",
        )
        is None
    )


def test_owner_list_is_user_and_session_scoped() -> None:
    first = start_bounded_training_session(
        duration_seconds=1,
        universe="canada",
        scope="user",
        owner_user_id="owner-list-a",
        owner_session_id="owner-session-a",
        requested_by_role="user",
    )

    start_bounded_training_session(
        duration_seconds=1,
        universe="canada",
        scope="user",
        owner_user_id="owner-list-b",
        owner_session_id="owner-session-b",
        requested_by_role="user",
    )

    runs = list_training_sessions_for_owner(
        owner_user_id="owner-list-a",
        owner_session_id="owner-session-a",
    )

    run_ids = {
        record["run_id"]
        for record in runs
    }

    assert first["run_id"] in run_ids

    assert all(
        record["owner_user_id"]
        == "owner-list-a"
        and record["owner_session_id"]
        == "owner-session-a"
        for record in runs
    )


def test_completed_contribution_contains_no_customer_identity() -> None:
    record = start_bounded_training_session(
        duration_seconds=1,
        universe="canada",
        requested_by="private-customer",
        source="pytest",
        scope="user",
        owner_user_id="private-user-id",
        owner_session_id="private-session-id",
        requested_by_role="user",
    )

    completed = wait_for_completion(
        record["run_id"]
    )

    contribution = completed[
        "sanitized_learning_contribution"
    ]

    serialized = str(
        contribution
    )

    assert "private-user-id" not in serialized
    assert "private-session-id" not in serialized
    assert "private-customer" not in serialized

    forbidden_keys = {
        "owner_user_id",
        "owner_session_id",
        "requested_by",
        "email",
        "display_name",
        "portfolio",
        "positions",
        "orders",
        "chat_messages",
        "access_token",
        "refresh_token",
    }

    assert not (
        forbidden_keys
        & set(contribution)
    )

    safety = contribution["safety"]

    assert (
        safety[
            "customer_identity_included"
        ]
        is False
    )

    assert (
        safety[
            "session_identity_included"
        ]
        is False
    )

    assert (
        safety[
            "portfolio_data_included"
        ]
        is False
    )

    assert (
        safety[
            "authentication_data_included"
        ]
        is False
    )


def test_admin_has_no_training_start_route() -> None:
    source = MAIN.read_text(
        encoding="utf-8",
    )

    assert (
        '@app.post(\n'
        '    "/api/v1/admin/training/runs"'
        not in source
    )

    assert (
        '"/api/v1/admin/training/health"'
        in source
    )

    assert (
        '"/api/v1/admin/training/failures"'
        in source
    )


def test_developer_has_system_training_start_route() -> None:
    source = MAIN.read_text(
        encoding="utf-8",
    )

    assert (
        '"/api/v1/developer/training/runs"'
        in source
    )

    assert (
        "_require_developer_training_role"
        in source
    )

    assert (
        'scope="system"'
        in source
    )


def test_user_routes_are_owner_scoped() -> None:
    source = MAIN.read_text(
        encoding="utf-8",
    )

    assert (
        '"/api/v1/training/runs"'
        in source
    )

    assert (
        "get_training_session_for_owner("
        in source
    )

    assert (
        "list_training_sessions_for_owner("
        in source
    )

    assert (
        "_training_principal_session("
        in source
    )


def test_admin_health_record_does_not_expose_owner_fields() -> None:
    source = SERVICE.read_text(
        encoding="utf-8",
    )

    start = source.index(
        "def _public_health_record("
    )

    end = source.index(
        "def _sanitized_learning_contribution("
    )

    function = source[start:end]

    assert '"owner_user_id"' not in function
    assert '"owner_session_id"' not in function
    assert '"requested_by"' not in function
