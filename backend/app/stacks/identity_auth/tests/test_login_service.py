from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import (
    AsyncMock,
    Mock,
)

import pytest

from backend.app.stacks.identity_auth.login_service import (
    LoginService,
)

from backend.app.stacks.identity_auth.service_contracts import (
    AuthenticationRejectedError,
    IssuedServiceToken,
    LoginCommand,
)


def issued(
    *,
    token: str,
    token_id: str,
) -> IssuedServiceToken:
    now = datetime.now(
        UTC
    )

    return IssuedServiceToken(
        token=token,
        token_id=token_id,
        issued_at=now,
        expires_at=(
            now
            + timedelta(
                minutes=30
            )
        ),
    )


def build_service(
    *,
    user=None,
    password_valid: bool = True,
):
    user_repository = Mock()

    user_repository.get_by_email = AsyncMock(
        return_value=user
    )

    refresh_repository = Mock()

    refresh_repository.create = AsyncMock()

    verify_password = Mock(
        return_value=password_valid
    )

    token_issuer = Mock()

    token_issuer.issue_access_token = AsyncMock(
        return_value=issued(
            token="access-token",
            token_id="access-id",
        )
    )

    token_issuer.issue_refresh_token = AsyncMock(
        return_value=issued(
            token="refresh-token",
            token_id="refresh-id",
        )
    )

    hash_refresh_token = Mock(
        return_value="a" * 64
    )

    commit = AsyncMock()
    rollback = AsyncMock()

    service = LoginService(
        user_repository=user_repository,
        refresh_session_repository=(
            refresh_repository
        ),
        verify_password=verify_password,
        token_issuer=token_issuer,
        hash_refresh_token=hash_refresh_token,
        dummy_password_hash="dummy-hash",
        commit=commit,
        rollback=rollback,
    )

    return (
        service,
        user_repository,
        refresh_repository,
        verify_password,
        token_issuer,
        hash_refresh_token,
        commit,
        rollback,
    )


def active_user():
    return SimpleNamespace(
        id="user-1",
        email_normalized="user@example.com",
        password_hash="stored-hash",
        status="active",
        is_active=True,
        must_change_password=False,
        role="owner",
        subscription_tier="internal",
    )


@pytest.mark.asyncio
async def test_valid_login_issues_separate_tokens_and_session() -> None:
    (
        service,
        user_repository,
        refresh_repository,
        verify_password,
        token_issuer,
        hash_refresh_token,
        commit,
        rollback,
    ) = build_service(
        user=active_user()
    )

    result = await service.login(
        LoginCommand(
            email=" User@Example.COM ",
            password="correct-password",
        )
    )

    user_repository.get_by_email.assert_awaited_once_with(
        "user@example.com"
    )

    verify_password.assert_called_once_with(
        "correct-password",
        "stored-hash",
    )

    token_issuer.issue_access_token.assert_awaited_once_with(
        subject="user-1",
        extra_claims={
            "authorization_role": "developer",
            "subscription_tier": "internal",
        },
    )

    token_issuer.issue_refresh_token.assert_awaited_once_with(
        subject="user-1",
        extra_claims={
            "authorization_role": "developer",
            "subscription_tier": "internal",
        },
    )

    hash_refresh_token.assert_called_once_with(
        "refresh-token"
    )

    refresh_repository.create.assert_awaited_once()

    created = refresh_repository.create.await_args.kwargs

    assert created[
        "user_id"
    ] == "user-1"

    assert created[
        "token_id"
    ] == "refresh-id"

    assert created[
        "token_hash"
    ] == "a" * 64

    assert "refresh-token" not in created.values()

    commit.assert_awaited_once()
    rollback.assert_not_awaited()

    assert result.access_token == "access-token"
    assert result.refresh_token == "refresh-token"
    assert result.access_token != result.refresh_token
    assert result.token_type == "bearer"


@pytest.mark.asyncio
async def test_unknown_user_and_wrong_password_share_error() -> None:
    unknown = build_service(
        user=None,
        password_valid=False,
    )

    wrong_password = build_service(
        user=active_user(),
        password_valid=False,
    )

    unknown_service = unknown[0]
    wrong_service = wrong_password[0]

    with pytest.raises(
        AuthenticationRejectedError
    ) as unknown_error:
        await unknown_service.login(
            LoginCommand(
                email="missing@example.com",
                password="wrong",
            )
        )

    with pytest.raises(
        AuthenticationRejectedError
    ) as password_error:
        await wrong_service.login(
            LoginCommand(
                email="user@example.com",
                password="wrong",
            )
        )

    assert str(
        unknown_error.value
    ) == str(
        password_error.value
    ) == "Authentication failed"

    unknown_verify = unknown[3]

    unknown_verify.assert_called_once_with(
        "wrong",
        "dummy-hash",
    )


@pytest.mark.asyncio
async def test_disabled_account_fails_closed() -> None:
    user = active_user()

    user.is_active = False

    (
        service,
        _,
        refresh_repository,
        _,
        token_issuer,
        _,
        commit,
        rollback,
    ) = build_service(
        user=user,
        password_valid=True,
    )

    with pytest.raises(
        AuthenticationRejectedError,
        match="Authentication failed",
    ):
        await service.login(
            LoginCommand(
                email="user@example.com",
                password="correct-password",
            )
        )

    token_issuer.issue_access_token.assert_not_awaited()

    refresh_repository.create.assert_not_awaited()

    commit.assert_not_awaited()
    rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_inactive_status_fails_closed() -> None:
    user = active_user()

    user.status = "disabled"

    service, _, _, _, token_issuer, _, commit, rollback = (
        build_service(
            user=user,
            password_valid=True,
        )
    )

    with pytest.raises(
        AuthenticationRejectedError,
        match="Authentication failed",
    ):
        await service.login(
            LoginCommand(
                email="user@example.com",
                password="correct-password",
            )
        )

    token_issuer.issue_access_token.assert_not_awaited()
    commit.assert_not_awaited()
    rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_refresh_session_failure_rolls_back() -> None:
    (
        service,
        _,
        refresh_repository,
        _,
        _,
        _,
        commit,
        rollback,
    ) = build_service(
        user=active_user()
    )

    refresh_repository.create.side_effect = RuntimeError(
        "database unavailable"
    )

    with pytest.raises(
        AuthenticationRejectedError,
        match="Authentication failed",
    ):
        await service.login(
            LoginCommand(
                email="user@example.com",
                password="correct-password",
            )
        )

    commit.assert_not_awaited()
    rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_identical_tokens_fail_closed() -> None:
    (
        service,
        _,
        refresh_repository,
        _,
        token_issuer,
        _,
        commit,
        rollback,
    ) = build_service(
        user=active_user()
    )

    token_issuer.issue_access_token.return_value = issued(
        token="same-token",
        token_id="access-id",
    )

    token_issuer.issue_refresh_token.return_value = issued(
        token="same-token",
        token_id="refresh-id",
    )

    with pytest.raises(
        AuthenticationRejectedError,
        match="Authentication failed",
    ):
        await service.login(
            LoginCommand(
                email="user@example.com",
                password="correct-password",
            )
        )

    refresh_repository.create.assert_not_awaited()
    commit.assert_not_awaited()
    rollback.assert_awaited_once()
