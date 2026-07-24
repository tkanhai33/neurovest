from __future__ import annotations

from datetime import (
    UTC,
    datetime,
    timedelta,
)
from types import SimpleNamespace

import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.stacks.identity_auth import (
    api_router,
    route_protection,
)

from backend.app.stacks.identity_auth.api_dependencies import (
    get_session_lifecycle_api_service,
    require_authenticated_principal,
)

from backend.app.stacks.identity_auth.service_contracts import (
    AuthenticationTokenPair,
)

from backend.app.stacks.identity_auth.session_lifecycle_service import (
    SessionLifecycleRejectedError,
)


def token_pair() -> AuthenticationTokenPair:
    now = datetime.now(
        UTC
    )

    return AuthenticationTokenPair(
        access_token="new-access-token",
        refresh_token="new-refresh-token",
        token_type="bearer",
        access_expires_at=(
            now
            + timedelta(
                minutes=15
            )
        ),
        refresh_expires_at=(
            now
            + timedelta(
                days=7
            )
        ),
    )


class FakeLifecycleService:
    def __init__(self) -> None:
        self.refreshed = []
        self.logged_out = []
        self.logout_all_users = []

    async def refresh(
        self,
        *,
        refresh_token: str,
    ) -> AuthenticationTokenPair:
        self.refreshed.append(
            refresh_token
        )

        return token_pair()

    async def logout(
        self,
        *,
        refresh_token: str,
    ) -> None:
        self.logged_out.append(
            refresh_token
        )

    async def logout_all(
        self,
        *,
        user_id: str,
    ) -> int:
        self.logout_all_users.append(
            user_id
        )

        return 3


def build_app(
    service,
    *,
    principal=None,
) -> FastAPI:
    app = FastAPI()

    app.middleware(
        "http"
    )(
        route_protection.enforce_route_policy
    )

    app.include_router(
        api_router.router
    )

    async def lifecycle_override():
        yield service

    app.dependency_overrides[
        get_session_lifecycle_api_service
    ] = lifecycle_override

    if principal is not None:
        app.dependency_overrides[
            require_authenticated_principal
        ] = lambda: principal

    return app


def test_lifecycle_route_policy_inventory() -> None:
    assert (
        route_protection.resolve_route_policy(
            "POST",
            "/auth/refresh",
        )
        == route_protection.PUBLIC
    )

    assert (
        route_protection.resolve_route_policy(
            "POST",
            "/auth/logout",
        )
        == route_protection.PUBLIC
    )

    assert (
        route_protection.resolve_route_policy(
            "POST",
            "/auth/logout-all",
        )
        == route_protection.AUTHENTICATED
    )


def test_refresh_returns_rotated_pair() -> None:
    service = FakeLifecycleService()

    client = TestClient(
        build_app(
            service
        )
    )

    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": "old-refresh-token",
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "token_type": "bearer",
        "access_token": "new-access-token",
        "refresh_token": "new-refresh-token",
    }

    assert service.refreshed == [
        "old-refresh-token",
    ]


def test_logout_revokes_current_refresh_session() -> None:
    service = FakeLifecycleService()

    client = TestClient(
        build_app(
            service
        )
    )

    response = client.post(
        "/auth/logout",
        json={
            "refresh_token": "refresh-token",
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "status": "logged_out",
    }

    assert service.logged_out == [
        "refresh-token",
    ]


def test_refresh_rejection_is_unauthorized() -> None:
    class RejectingService(
        FakeLifecycleService
    ):
        async def refresh(
            self,
            *,
            refresh_token: str,
        ):
            raise SessionLifecycleRejectedError(
                "rejected"
            )

    client = TestClient(
        build_app(
            RejectingService()
        )
    )

    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": "invalid",
        },
    )

    assert response.status_code == 401

    assert response.headers[
        "www-authenticate"
    ] == "Bearer"


def test_logout_rejection_is_unauthorized() -> None:
    class RejectingService(
        FakeLifecycleService
    ):
        async def logout(
            self,
            *,
            refresh_token: str,
        ) -> None:
            raise SessionLifecycleRejectedError(
                "rejected"
            )

    client = TestClient(
        build_app(
            RejectingService()
        )
    )

    response = client.post(
        "/auth/logout",
        json={
            "refresh_token": "invalid",
        },
    )

    assert response.status_code == 401


def test_logout_all_uses_access_principal_subject(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = FakeLifecycleService()

    principal = SimpleNamespace(
        subject="user-123",
        token_id="access-jti",
        claims={},
    )

    monkeypatch.setattr(
        route_protection,
        "authenticate_bearer_credentials",
        lambda credentials: principal,
    )

    async def load_identity_state(
        user_id: str,
    ) -> dict[str, object]:
        assert user_id == 'user-123'

        return {
            "is_active": True,
            "status": "active",
            "role": 'user',
            "must_change_password": False,
        }

    monkeypatch.setattr(
        route_protection,
        "_load_identity_authorization_state",
        load_identity_state,
    )

    client = TestClient(
        build_app(
            service,
            principal=principal,
        )
    )

    response = client.post(
        "/auth/logout-all",
        headers={
            "Authorization": "Bearer access-token",
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "status": "logged_out_all",
        "revoked_sessions": 3,
    }

    assert service.logout_all_users == [
        "user-123",
    ]


def test_logout_all_rejects_missing_access_token() -> None:
    service = FakeLifecycleService()

    client = TestClient(
        build_app(
            service
        )
    )

    response = client.post(
        "/auth/logout-all",
    )

    assert response.status_code == 401


def test_refresh_request_forbids_extra_fields() -> None:
    service = FakeLifecycleService()

    client = TestClient(
        build_app(
            service
        )
    )

    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": "refresh-token",
            "role": "admin",
        },
    )

    assert response.status_code == 422


def test_logout_request_forbids_extra_fields() -> None:
    service = FakeLifecycleService()

    client = TestClient(
        build_app(
            service
        )
    )

    response = client.post(
        "/auth/logout",
        json={
            "refresh_token": "refresh-token",
            "user_id": "someone-else",
        },
    )

    assert response.status_code == 422
