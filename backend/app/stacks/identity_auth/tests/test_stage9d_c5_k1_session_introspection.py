from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from fastapi.routing import APIRoute

from backend.app.stacks.identity_auth.api_router import (
    router as auth_router,
    session_introspection,
)
from backend.app.stacks.identity_auth.route_protection import (
    AUTHENTICATED,
    resolve_route_policy,
)
from backend.app.stacks.identity_auth.session_introspection import (
    get_session_introspection,
)


class FakeIdentityUserRepository:
    def __init__(self, user=None) -> None:
        self.user = user
        self.requested_user_id: str | None = None

    async def get_by_id(self, user_id: str):
        self.requested_user_id = user_id
        return self.user


def identity_user(
    *,
    user_id: str = "user-1",
    role: str = "user",
    subscription_tier: str = "free",
    status: str = "active",
    is_active: bool = True,
    must_change_password: bool = False,
):
    return SimpleNamespace(
        id=user_id,
        role=role,
        subscription_tier=subscription_tier,
        status=status,
        is_active=is_active,
        must_change_password=must_change_password,
        display_name="Test User",
        email_normalized="user@example.com",
    )


def test_canonical_router_contains_introspection_route() -> None:
    matching = [
        route
        for route in auth_router.routes
        if (
            isinstance(route, APIRoute)
            and route.path == "/auth/introspection"
        )
    ]

    assert len(matching) == 1
    assert matching[0].methods == {"GET"}
    assert matching[0].name == "session_introspection"


def test_introspection_route_policy_is_authenticated() -> None:
    assert (
        resolve_route_policy(
            "GET",
            "/auth/introspection",
        )
        == AUTHENTICATED
    )

    assert (
        resolve_route_policy(
            "POST",
            "/auth/introspection",
        )
        is None
    )


@pytest.mark.asyncio
async def test_introspection_uses_principal_subject() -> None:
    repository = FakeIdentityUserRepository(
        identity_user()
    )

    response = await session_introspection(
        principal=SimpleNamespace(
            subject="user-1"
        ),
        session_repo=repository,
    )

    assert repository.requested_user_id == "user-1"
    assert response["user_id"] == "user-1"
    assert response["role"] == "user"
    assert response["subscription_tier"] == "free"
    assert response["status"] == "active"
    assert response["is_active"] is True
    assert response["must_change_password"] is False
    assert "broker.live" not in response["permissions"]


@pytest.mark.asyncio
async def test_missing_identity_fails_closed() -> None:
    repository = FakeIdentityUserRepository()

    with pytest.raises(HTTPException) as exc_info:
        await get_session_introspection(
            "missing-user",
            repository,
        )

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_inactive_identity_fails_closed() -> None:
    repository = FakeIdentityUserRepository(
        identity_user(
            is_active=False
        )
    )

    with pytest.raises(HTTPException) as exc_info:
        await get_session_introspection(
            "user-1",
            repository,
        )

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_disabled_identity_fails_closed() -> None:
    repository = FakeIdentityUserRepository(
        identity_user(
            status="disabled"
        )
    )

    with pytest.raises(HTTPException) as exc_info:
        await get_session_introspection(
            "user-1",
            repository,
        )

    assert exc_info.value.status_code == 403
