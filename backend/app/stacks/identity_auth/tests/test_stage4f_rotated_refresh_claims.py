from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from backend.app.stacks.identity_auth.session_lifecycle_service import (
    SessionLifecycleService,
    ValidatedRefreshIdentity,
)

from backend.app.stacks.identity_auth.service_contracts import (
    IssuedServiceToken,
)


def issued(
    *,
    token: str,
    token_id: str,
):
    from datetime import UTC, datetime, timedelta

    now = datetime.now(UTC)

    return IssuedServiceToken(
        token=token,
        token_id=token_id,
        issued_at=now,
        expires_at=now + timedelta(hours=1),
    )


@pytest.mark.asyncio
async def test_rotated_refresh_token_receives_canonical_claims() -> None:
    refresh_repository = Mock()

    refresh_repository.get_by_token_id = AsyncMock(
        return_value=SimpleNamespace(
            user_id="user-1",
            token_id="old-refresh-id",
            token_hash="stored-refresh-hash",
        )
    )

    refresh_repository.create = AsyncMock()
    refresh_repository.revoke = AsyncMock()

    refresh_service = Mock()
    refresh_service.rotate = AsyncMock()

    token_issuer = Mock()

    token_issuer.issue_access_token = AsyncMock(
        return_value=issued(
            token="new-access-token",
            token_id="new-access-id",
        )
    )

    token_issuer.issue_refresh_token = AsyncMock(
        return_value=issued(
            token="new-refresh-token",
            token_id="new-refresh-id",
        )
    )

    user_repository = Mock()

    user_repository.get_by_id = AsyncMock(
        return_value=SimpleNamespace(
            id="user-1",
            role="owner",
            subscription_tier="free",
            status="active",
            is_active=True,
        )
    )

    commit = AsyncMock()
    rollback = AsyncMock()

    service = SessionLifecycleService(
        refresh_repository=refresh_repository,
        refresh_service=refresh_service,
        token_issuer=token_issuer,
        validate_refresh_token=Mock(
            return_value=ValidatedRefreshIdentity(
                subject="user-1",
                token_id="old-refresh-id",
            )
        ),
        hash_refresh_token=Mock(
            return_value="replacement-hash"
        ),
        verify_refresh_token=Mock(
            return_value=True
        ),
        commit=commit,
        rollback=rollback,
        access_revocation_repository=Mock(),
        user_repository=user_repository,
    )

    await service.refresh(
        refresh_token="old-refresh-token"
    )

    expected_claims = {
        "authorization_role": "developer",
        "subscription_tier": "free",
    }

    token_issuer.issue_access_token.assert_awaited_once_with(
        subject="user-1",
        extra_claims=expected_claims,
    )

    token_issuer.issue_refresh_token.assert_awaited_once_with(
        subject="user-1",
        extra_claims=expected_claims,
    )
