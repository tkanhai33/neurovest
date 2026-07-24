from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from backend.app.stacks.identity_auth.login_service import (
    LoginService,
)

from backend.app.stacks.identity_auth.service_contracts import (
    IssuedServiceToken,
    LoginCommand,
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
        expires_at=(
            now
            + timedelta(
                minutes=30
            )
        ),
    )


@pytest.mark.asyncio
async def test_login_forwards_canonical_claims_to_both_tokens() -> None:
    user = SimpleNamespace(
        id="owner-1",
        email_normalized="dev@neurovest.com",
        password_hash="stored-hash",
        status="active",
        is_active=True,
        role="owner",
        subscription_tier="free",
        must_change_password=False,
    )

    user_repository = Mock()
    user_repository.get_by_email = AsyncMock(
        return_value=user
    )

    refresh_repository = Mock()
    refresh_repository.create = AsyncMock()

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

    service = LoginService(
        user_repository=user_repository,
        refresh_session_repository=refresh_repository,
        verify_password=Mock(
            return_value=True
        ),
        token_issuer=token_issuer,
        hash_refresh_token=Mock(
            return_value="a" * 64
        ),
        dummy_password_hash="dummy",
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    result = await service.login(
        LoginCommand(
            email="dev@neurovest.com",
            password="correct-password",
        )
    )

    expected_claims = {
        "authorization_role": "developer",
        "subscription_tier": "free",
    }

    token_issuer.issue_access_token.assert_awaited_once_with(
        subject="owner-1",
        extra_claims=expected_claims,
    )

    token_issuer.issue_refresh_token.assert_awaited_once_with(
        subject="owner-1",
        extra_claims=expected_claims,
    )

    assert result.access_token == "access-token"
    assert result.refresh_token == "refresh-token"
