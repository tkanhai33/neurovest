from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from backend.app.stacks.identity_auth.login_service import (
    LoginService,
)

from backend.app.stacks.identity_auth.service_contracts import (
    AuthenticationRejectedError,
    IssuedServiceToken,
    LoginCommand,
)

from backend.app.stacks.identity_auth.session_lifecycle_service import (
    SessionLifecycleRejectedError,
    SessionLifecycleService,
    ValidatedRefreshIdentity,
)


def issued(
    *,
    token: str,
    token_id: str,
) -> IssuedServiceToken:
    now = datetime.now(UTC)

    return IssuedServiceToken(
        token=token,
        token_id=token_id,
        issued_at=now,
        expires_at=now + timedelta(minutes=30),
    )


def active_user(
    *,
    role: str = "owner",
    tier: str = "internal",
):
    return SimpleNamespace(
        id="user-1",
        email_normalized="user@example.com",
        password_hash="stored-hash",
        status="active",
        is_active=True,
        must_change_password=False,
        role=role,
        subscription_tier=tier,
    )


@pytest.mark.asyncio
async def test_login_issues_canonical_role_and_tier_claims() -> None:
    user_repository = Mock()
    user_repository.get_by_email = AsyncMock(
        return_value=active_user()
    )

    refresh_repository = Mock()
    refresh_repository.create = AsyncMock()

    issuer = Mock()
    issuer.issue_access_token = AsyncMock(
        return_value=issued(
            token="access",
            token_id="access-id",
        )
    )
    issuer.issue_refresh_token = AsyncMock(
        return_value=issued(
            token="refresh",
            token_id="refresh-id",
        )
    )

    service = LoginService(
        user_repository=user_repository,
        refresh_session_repository=refresh_repository,
        verify_password=Mock(return_value=True),
        token_issuer=issuer,
        hash_refresh_token=Mock(
            return_value="a" * 64
        ),
        dummy_password_hash="dummy",
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    await service.login(
        LoginCommand(
            email="user@example.com",
            password="password",
        )
    )

    issuer.issue_access_token.assert_awaited_once_with(
        subject="user-1",
        extra_claims={
            "authorization_role": "developer",
            "subscription_tier": "internal",
        },
    )

    issuer.issue_refresh_token.assert_awaited_once_with(
        subject="user-1",
        extra_claims={
            "authorization_role": "developer",
            "subscription_tier": "internal",
        },
    )


@pytest.mark.asyncio
async def test_login_rejects_invalid_stored_role() -> None:
    user_repository = Mock()
    user_repository.get_by_email = AsyncMock(
        return_value=active_user(
            role="untrusted_superuser",
        )
    )

    issuer = Mock()
    issuer.issue_access_token = AsyncMock()
    issuer.issue_refresh_token = AsyncMock()

    service = LoginService(
        user_repository=user_repository,
        refresh_session_repository=Mock(),
        verify_password=Mock(return_value=True),
        token_issuer=issuer,
        hash_refresh_token=Mock(),
        dummy_password_hash="dummy",
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    with pytest.raises(
        AuthenticationRejectedError,
        match="Authentication failed",
    ):
        await service.login(
            LoginCommand(
                email="user@example.com",
                password="password",
            )
        )

    issuer.issue_access_token.assert_not_awaited()


@pytest.mark.asyncio
async def test_refresh_uses_current_user_claims() -> None:
    refresh_record = SimpleNamespace(
        user_id="user-1",
        token_id="refresh-id",
        token_hash="stored-refresh-hash",
    )

    refresh_repository = Mock()
    refresh_repository.get_by_token_id = AsyncMock(
        return_value=refresh_record
    )

    user_repository = Mock()
    user_repository.get_by_id = AsyncMock(
        return_value=active_user(
            role="admin",
            tier="pro",
        )
    )

    issuer = Mock()
    issuer.issue_access_token = AsyncMock(
        return_value=issued(
            token="new-access",
            token_id="new-access-id",
        )
    )
    issuer.issue_refresh_token = AsyncMock(
        return_value=issued(
            token="new-refresh",
            token_id="new-refresh-id",
        )
    )

    refresh_service = Mock()
    refresh_service.rotate = AsyncMock()

    service = SessionLifecycleService(
        refresh_repository=refresh_repository,
        user_repository=user_repository,
        refresh_service=refresh_service,
        token_issuer=issuer,
        validate_refresh_token=Mock(
            return_value=ValidatedRefreshIdentity(
                subject="user-1",
                token_id="refresh-id",
            )
        ),
        hash_refresh_token=Mock(
            return_value="b" * 64
        ),
        verify_refresh_token=Mock(
            return_value=True
        ),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    await service.refresh(
        refresh_token="original-refresh"
    )

    user_repository.get_by_id.assert_awaited_once_with(
        "user-1"
    )

    issuer.issue_access_token.assert_awaited_once_with(
        subject="user-1",
        extra_claims={
            "authorization_role": "admin",
            "subscription_tier": "pro",
        },
    )

    issuer.issue_refresh_token.assert_awaited_once_with(
        subject="user-1",
        extra_claims={
            "authorization_role": "admin",
            "subscription_tier": "pro",
        },
    )


@pytest.mark.asyncio
async def test_refresh_rejects_missing_current_user() -> None:
    refresh_record = SimpleNamespace(
        user_id="user-1",
        token_id="refresh-id",
        token_hash="stored-refresh-hash",
    )

    refresh_repository = Mock()
    refresh_repository.get_by_token_id = AsyncMock(
        return_value=refresh_record
    )

    user_repository = Mock()
    user_repository.get_by_id = AsyncMock(
        return_value=None
    )

    issuer = Mock()
    issuer.issue_access_token = AsyncMock()
    issuer.issue_refresh_token = AsyncMock()

    service = SessionLifecycleService(
        refresh_repository=refresh_repository,
        user_repository=user_repository,
        refresh_service=Mock(),
        token_issuer=issuer,
        validate_refresh_token=Mock(
            return_value=ValidatedRefreshIdentity(
                subject="user-1",
                token_id="refresh-id",
            )
        ),
        hash_refresh_token=Mock(),
        verify_refresh_token=Mock(
            return_value=True
        ),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    with pytest.raises(
        SessionLifecycleRejectedError,
        match="Session lifecycle request was rejected",
    ):
        await service.refresh(
            refresh_token="original-refresh"
        )

    issuer.issue_access_token.assert_not_awaited()
    issuer.issue_refresh_token.assert_not_awaited()
