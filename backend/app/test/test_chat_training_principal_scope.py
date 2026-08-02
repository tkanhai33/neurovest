from types import SimpleNamespace
from unittest.mock import patch

from backend.app.stacks.chat_public.chat_runtime import (
    handle_chat_message,
)


MESSAGE = (
    "Run a training session for "
    "2 minutes on all Canadian symbols."
)


def principal(
    *,
    subject: str,
    role: str,
    session: str,
):
    return SimpleNamespace(
        subject=subject,
        role=role,
        token_id=session,
        claims={
            "sub": subject,
            "authorization_role": role,
            "jti": session,
        },
    )


def fake_run(
    *,
    run_id: str,
    duration_seconds: int = 120,
):
    return {
        "run_id": run_id,
        "duration_seconds":
            duration_seconds,
        "status": "queued",
    }


def test_user_chat_starts_owned_session_run() -> None:
    actor = principal(
        subject="customer-a",
        role="user",
        session="session-a",
    )

    with patch(
        "backend.app.stacks.chat_public."
        "chat_runtime."
        "start_bounded_training_session",
        return_value=fake_run(
            run_id="user-run-a"
        ),
    ) as start:
        result = handle_chat_message(
            MESSAGE,
            principal=actor,
        )

    start.assert_called_once_with(
        duration_seconds=120,
        universe="canada",
        requested_by="customer-a",
        source="authenticated_user_chat",
        scope="user",
        owner_user_id="customer-a",
        owner_session_id="session-a",
        requested_by_role="user",
    )

    assert result["status"] == "ok"
    assert result["training_run"][
        "run_id"
    ] == "user-run-a"


def test_developer_chat_starts_system_run() -> None:
    actor = principal(
        subject="developer-a",
        role="developer",
        session="developer-session-a",
    )

    with patch(
        "backend.app.stacks.chat_public."
        "chat_runtime."
        "start_bounded_training_session",
        return_value=fake_run(
            run_id="system-run-a"
        ),
    ) as start:
        result = handle_chat_message(
            MESSAGE,
            principal=actor,
        )

    start.assert_called_once_with(
        duration_seconds=120,
        universe="canada",
        requested_by="developer-a",
        source=(
            "authenticated_developer_chat"
        ),
        scope="system",
        owner_user_id=None,
        owner_session_id=None,
        requested_by_role="developer",
    )

    assert result["status"] == "ok"
    assert result["training_run"][
        "run_id"
    ] == "system-run-a"


def test_owner_chat_starts_system_run() -> None:
    actor = principal(
        subject="owner-a",
        role="owner",
        session="owner-session-a",
    )

    with patch(
        "backend.app.stacks.chat_public."
        "chat_runtime."
        "start_bounded_training_session",
        return_value=fake_run(
            run_id="owner-system-run"
        ),
    ) as start:
        result = handle_chat_message(
            MESSAGE,
            principal=actor,
        )

    start.assert_called_once_with(
        duration_seconds=120,
        universe="canada",
        requested_by="owner-a",
        source=(
            "authenticated_developer_chat"
        ),
        scope="system",
        owner_user_id=None,
        owner_session_id=None,
        requested_by_role="owner",
    )

    assert result["status"] == "ok"


def test_admin_chat_cannot_start_training() -> None:
    actor = principal(
        subject="admin-a",
        role="admin",
        session="admin-session-a",
    )

    with patch(
        "backend.app.stacks.chat_public."
        "chat_runtime."
        "start_bounded_training_session",
    ) as start:
        result = handle_chat_message(
            MESSAGE,
            principal=actor,
        )

    start.assert_not_called()

    assert result["status"] == "blocked"

    assert result["error"] == (
        "administrator_training_start_denied"
    )

    assert (
        "cannot start training sessions"
        in result["response"]["message"]
    )


def test_missing_principal_fails_closed() -> None:
    with patch(
        "backend.app.stacks.chat_public."
        "chat_runtime."
        "start_bounded_training_session",
    ) as start:
        result = handle_chat_message(
            MESSAGE,
            principal=None,
        )

    start.assert_not_called()

    assert result["status"] == "blocked"

    assert result["error"] == (
        "authenticated_training_subject_missing"
    )


def test_user_without_session_fails_closed() -> None:
    actor = SimpleNamespace(
        subject="customer-no-session",
        role="user",
        claims={
            "sub":
                "customer-no-session",
            "authorization_role":
                "user",
        },
    )

    with patch(
        "backend.app.stacks.chat_public."
        "chat_runtime."
        "start_bounded_training_session",
    ) as start:
        result = handle_chat_message(
            MESSAGE,
            principal=actor,
        )

    start.assert_not_called()

    assert result["status"] == "blocked"

    assert result["error"] == (
        "authenticated_training_session_missing"
    )


def test_system_scope_never_receives_customer_session() -> None:
    actor = principal(
        subject="developer-b",
        role="developer",
        session="private-dev-session",
    )

    with patch(
        "backend.app.stacks.chat_public."
        "chat_runtime."
        "start_bounded_training_session",
        return_value=fake_run(
            run_id="system-run-b"
        ),
    ) as start:
        handle_chat_message(
            MESSAGE,
            principal=actor,
        )

    kwargs = start.call_args.kwargs

    assert kwargs["scope"] == "system"
    assert kwargs["owner_user_id"] is None
    assert kwargs["owner_session_id"] is None


def test_chat_runtime_source_passes_principal() -> None:
    from pathlib import Path

    source = Path(
        "backend/app/stacks/chat_public/"
        "chat_runtime.py"
    ).read_text(
        encoding="utf-8",
    )

    assert (
        "runtime_result = handle_chat_message("
        in source
    )

    assert (
        "        principal=principal,"
        in source
    )
