from __future__ import annotations

from datetime import (
    UTC,
    datetime,
    timedelta,
)
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from backend.app.stacks.identity_auth.session_lifecycle_service import (
    SessionLifecycleService,
    ValidatedRefreshIdentity,
)


@pytest.mark.asyncio
async def test_logout_persists_access_and_refresh_revocation_before_commit() -> None:
    events: list[str] = []

    refresh_repository = Mock()
    refresh_service = Mock()
    access_repository = Mock()

    refresh_record = SimpleNamespace(
        user_id="user-1",
        token_hash="stored-hash",
    )

    refresh_repository.get_by_token_id = AsyncMock(
        return_value=refresh_record
    )

    refresh_service.logout = AsyncMock(
        side_effect=lambda **_: events.append(
            "refresh-revoked"
        )
    )

    access_repository.revoke = AsyncMock(
        side_effect=lambda **_: events.append(
            "access-revoked"
        )
    )

    async def commit() -> None:
        events.append("commit")

    rollback = AsyncMock()

    service = SessionLifecycleService(
        refresh_repository=refresh_repository,
        refresh_service=refresh_service,
        token_issuer=Mock(),
        validate_refresh_token=lambda _: (
            ValidatedRefreshIdentity(
                subject="user-1",
                token_id="refresh-jti",
            )
        ),
        hash_refresh_token=lambda value: value,
        verify_refresh_token=lambda *_: True,
        commit=commit,
        rollback=rollback,
        access_revocation_repository=(
            access_repository
        ),
    )

    now = datetime.now(UTC)

    await service.logout(
        refresh_token="refresh-token",
        access_token_id="access-jti",
        access_user_id="user-1",
        access_issued_at=(
            now
            - timedelta(minutes=1)
        ),
        access_expires_at=(
            now
            + timedelta(minutes=14)
        ),
    )

    assert events == [
        "access-revoked",
        "refresh-revoked",
        "commit",
    ]

    access_repository.revoke.assert_awaited_once()

    kwargs = (
        access_repository.revoke.await_args.kwargs
    )

    assert kwargs["token_id"] == "access-jti"
    assert kwargs["user_id"] == "user-1"
    assert kwargs["reason"] == "logout"

    rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_logout_rolls_back_both_revocations_on_failure() -> None:
    refresh_repository = Mock()
    refresh_service = Mock()
    access_repository = Mock()

    refresh_repository.get_by_token_id = AsyncMock(
        return_value=SimpleNamespace(
            user_id="user-1",
            token_hash="stored-hash",
        )
    )

    refresh_service.logout = AsyncMock(
        side_effect=RuntimeError(
            "refresh failure"
        )
    )

    access_repository.revoke = AsyncMock()

    commit = AsyncMock()
    rollback = AsyncMock()

    service = SessionLifecycleService(
        refresh_repository=refresh_repository,
        refresh_service=refresh_service,
        token_issuer=Mock(),
        validate_refresh_token=lambda _: (
            ValidatedRefreshIdentity(
                subject="user-1",
                token_id="refresh-jti",
            )
        ),
        hash_refresh_token=lambda value: value,
        verify_refresh_token=lambda *_: True,
        commit=commit,
        rollback=rollback,
        access_revocation_repository=(
            access_repository
        ),
    )

    now = datetime.now(UTC)

    with pytest.raises(Exception):
        await service.logout(
            refresh_token="refresh-token",
            access_token_id="access-jti",
            access_user_id="user-1",
            access_issued_at=now,
            access_expires_at=(
                now
                + timedelta(minutes=15)
            ),
        )

    access_repository.revoke.assert_awaited_once()
    rollback.assert_awaited_once()
    commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_logout_rejects_access_refresh_subject_mismatch() -> None:
    refresh_repository = Mock()
    refresh_service = Mock()
    access_repository = Mock()

    refresh_repository.get_by_token_id = AsyncMock(
        return_value=SimpleNamespace(
            user_id="user-1",
            token_hash="stored-hash",
        )
    )

    refresh_service.logout = AsyncMock()
    access_repository.revoke = AsyncMock()

    commit = AsyncMock()
    rollback = AsyncMock()

    service = SessionLifecycleService(
        refresh_repository=refresh_repository,
        refresh_service=refresh_service,
        token_issuer=Mock(),
        validate_refresh_token=lambda _: (
            ValidatedRefreshIdentity(
                subject="user-1",
                token_id="refresh-jti",
            )
        ),
        hash_refresh_token=lambda value: value,
        verify_refresh_token=lambda *_: True,
        commit=commit,
        rollback=rollback,
        access_revocation_repository=(
            access_repository
        ),
    )

    now = datetime.now(UTC)

    with pytest.raises(Exception):
        await service.logout(
            refresh_token="refresh-token",
            access_token_id="access-jti",
            access_user_id="different-user",
            access_issued_at=now,
            access_expires_at=(
                now
                + timedelta(minutes=15)
            ),
        )

    access_repository.revoke.assert_not_awaited()
    refresh_service.logout.assert_not_awaited()
    rollback.assert_awaited_once()
    commit.assert_not_awaited()
