from __future__ import annotations

from datetime import (
    UTC,
    datetime,
    timedelta,
)
from types import SimpleNamespace
from unittest.mock import (
    AsyncMock,
    Mock,
)

import pytest
from fastapi.routing import APIRoute

from backend.app.stacks.identity_auth.access_token_revocation_cleanup_service import (
    AccessTokenRevocationCleanupService,
)
from backend.app.stacks.identity_auth.admin_read_models import (
    AdministrativeReadService,
)
from backend.app.stacks.identity_auth.admin_read_router import (
    router,
)


def test_revocation_routes_are_get_only() -> None:
    expected = {
        (
            "/api/v1/admin/"
            "access-token-revocations"
        ),
        (
            "/api/v1/admin/"
            "access-token-revocations/"
            "{revocation_id}"
        ),
    }

    routes = {
        route.path: set(
            route.methods or set()
        )
        for route in router.routes
        if isinstance(
            route,
            APIRoute,
        )
        and route.path in expected
    }

    assert set(routes) == expected

    for path in expected:
        assert routes[path] == {
            "GET",
        }


def test_revocation_summary_exposes_no_jti() -> None:
    now = datetime.now(
        UTC
    ).replace(
        tzinfo=None
    )

    record = SimpleNamespace(
        id="revocation-1",
        token_id="secret-jti",
        user_id="user-1",
        issued_at=(
            now
            - timedelta(
                minutes=5
            )
        ),
        expires_at=(
            now
            + timedelta(
                minutes=10
            )
        ),
        revoked_at=now,
        reason="logout",
        created_at=now,
    )

    summary = (
        AdministrativeReadService
        ._revocation_summary(
            record
        )
    )

    payload = summary.model_dump()

    assert "token_id" not in payload
    assert "access_token" not in payload
    assert "refresh_token" not in payload
    assert "token_hash" not in payload
    assert "password" not in payload
    assert "password_hash" not in payload

    assert payload["id"] == "revocation-1"
    assert payload["user_id"] == "user-1"
    assert payload["state"] == "active"


@pytest.mark.asyncio
async def test_cleanup_service_commits_success() -> None:
    session = Mock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    service = AccessTokenRevocationCleanupService(
        session
    )

    service._repository.cleanup_expired = AsyncMock(
        return_value=3
    )

    deleted = await service.cleanup_expired()

    assert deleted == 3

    (
        service._repository.cleanup_expired
        .assert_awaited_once()
    )

    session.commit.assert_awaited_once()
    session.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_cleanup_service_rolls_back_failure() -> None:
    session = Mock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    service = AccessTokenRevocationCleanupService(
        session
    )

    service._repository.cleanup_expired = AsyncMock(
        side_effect=RuntimeError(
            "cleanup failed"
        )
    )

    with pytest.raises(
        RuntimeError,
        match="cleanup failed",
    ):
        await service.cleanup_expired()

    session.commit.assert_not_awaited()
    session.rollback.assert_awaited_once()
