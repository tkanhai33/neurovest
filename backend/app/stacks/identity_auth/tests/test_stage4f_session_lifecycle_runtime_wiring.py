from __future__ import annotations

from unittest.mock import Mock, patch

from backend.app.stacks.identity_auth.runtime_adapter import (
    build_session_lifecycle_runtime,
)


def test_session_lifecycle_runtime_builds_user_repository() -> None:
    session = Mock(
        name="identity_session"
    )

    with (
        patch(
            "backend.app.stacks.identity_auth.runtime_adapter."
            "IdentityUserRepository"
        ) as user_repository_type,
        patch(
            "backend.app.stacks.identity_auth.runtime_adapter."
            "RefreshSessionRepository"
        ) as refresh_repository_type,
        patch(
            "backend.app.stacks.identity_auth.runtime_adapter."
            "AccessTokenRevocationRepository"
        ) as revocation_repository_type,
    ):
        service = build_session_lifecycle_runtime(
            session
        )

    user_repository_type.assert_called_once_with(
        session
    )

    refresh_repository_type.assert_called_once_with(
        session
    )

    revocation_repository_type.assert_called_once_with(
        session
    )

    assert (
        service._user_repository
        is user_repository_type.return_value
    )


def test_session_lifecycle_runtime_uses_one_shared_session() -> None:
    session = Mock(
        name="shared_session"
    )

    with (
        patch(
            "backend.app.stacks.identity_auth.runtime_adapter."
            "IdentityUserRepository"
        ) as user_repository_type,
        patch(
            "backend.app.stacks.identity_auth.runtime_adapter."
            "RefreshSessionRepository"
        ) as refresh_repository_type,
        patch(
            "backend.app.stacks.identity_auth.runtime_adapter."
            "AccessTokenRevocationRepository"
        ) as revocation_repository_type,
    ):
        build_session_lifecycle_runtime(
            session
        )

    assert (
        user_repository_type.call_args.args
        == (session,)
    )

    assert (
        refresh_repository_type.call_args.args
        == (session,)
    )

    assert (
        revocation_repository_type.call_args.args
        == (session,)
    )
