from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, Mock

import pytest

from backend.app.stacks.identity_auth.models import (
    IdentityRefreshSession,
)

from backend.app.stacks.identity_auth.session_service import (
    RefreshSessionService,
    RefreshTokenReuseDetectedError,
)


def make_record(
    *,
    revoked: bool = False,
) -> IdentityRefreshSession:
    now = datetime.now(
        UTC
    )

    return IdentityRefreshSession(
        id="session-1",
        user_id="user-1",
        token_id="token-1",
        token_hash="a" * 64,
        family_id="family-1",
        issued_at=(
            now
            - timedelta(
                minutes=1
            )
        ),
        expires_at=(
            now
            + timedelta(
                minutes=30
            )
        ),
        revoked_at=(
            now
            if revoked
            else None
        ),
        created_at=now,
    )


@pytest.mark.asyncio
async def test_rotation_preserves_family_and_revokes_old() -> None:
    session = Mock()

    service = RefreshSessionService(
        session
    )

    current = make_record()

    replacement = make_record()

    replacement.id = "session-2"
    replacement.token_id = "token-2"

    service._repository.get_by_token_id = AsyncMock(
        return_value=current
    )

    service._repository.create = AsyncMock(
        return_value=replacement
    )

    service._repository.revoke = AsyncMock()

    result = await service.rotate(
        current_token_id="token-1",
        replacement_token_id="token-2",
        replacement_token_hash="b" * 64,
        replacement_issued_at=datetime.now(
            UTC
        ),
        replacement_expires_at=(
            datetime.now(
                UTC
            )
            + timedelta(
                hours=1
            )
        ),
    )

    assert result.previous_token_id == "token-1"
    assert result.replacement_token_id == "token-2"
    assert result.family_id == "family-1"

    service._repository.revoke.assert_awaited_once()


@pytest.mark.asyncio
async def test_reuse_revokes_entire_family() -> None:
    session = Mock()

    service = RefreshSessionService(
        session
    )

    revoked = make_record(
        revoked=True
    )

    service._repository.get_by_token_id = AsyncMock(
        return_value=revoked
    )

    service._repository.revoke_family = AsyncMock(
        return_value=1
    )

    with pytest.raises(
        RefreshTokenReuseDetectedError
    ):
        await service.rotate(
            current_token_id="token-1",
            replacement_token_id="token-2",
            replacement_token_hash="b" * 64,
            replacement_issued_at=datetime.now(
                UTC
            ),
            replacement_expires_at=(
                datetime.now(
                    UTC
                )
                + timedelta(
                    hours=1
                )
            ),
        )

    service._repository.revoke_family.assert_awaited_once()


@pytest.mark.asyncio
async def test_logout_is_idempotent() -> None:
    session = Mock()

    service = RefreshSessionService(
        session
    )

    service._repository.get_by_token_id = AsyncMock(
        return_value=None
    )

    service._repository.revoke = AsyncMock()

    await service.logout(
        token_id="missing-token"
    )

    service._repository.revoke.assert_not_awaited()
