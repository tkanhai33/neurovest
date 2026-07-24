from __future__ import annotations

from types import SimpleNamespace

import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.stacks.identity_auth import (
    route_protection,
)


def build_test_app() -> FastAPI:
    app = FastAPI()

    app.middleware(
        "http"
    )(
        route_protection.enforce_route_policy
    )

    @app.get(
        "/api/v1/analytics"
    )
    async def analytics():
        return {
            "ok": True,
        }

    @app.post(
        "/api/v1/admin/backup"
    )
    async def admin_backup():
        return {
            "ok": True,
        }

    @app.get(
        "/api/v1/market-data/status"
    )
    async def market_status():
        return {
            "ok": True,
        }

    return app


def test_route_policy_inventory() -> None:
    assert (
        route_protection.resolve_route_policy(
            "POST",
            "/auth/register",
        )
        == route_protection.PUBLIC
    )

    assert (
        route_protection.resolve_route_policy(
            "POST",
            "/auth/login",
        )
        == route_protection.PUBLIC
    )

    assert (
        route_protection.resolve_route_policy(
            "GET",
            "/api/v1/analytics",
        )
        == route_protection.AUTHENTICATED
    )

    assert (
        route_protection.resolve_route_policy(
            "GET",
            "/api/v1/strategy/decision/AAPL",
        )
        == route_protection.AUTHENTICATED
    )

    assert (
        route_protection.resolve_route_policy(
            "POST",
            "/api/v1/admin/backup",
        )
        == route_protection.ADMIN_ONLY
    )


def test_public_route_requires_no_token() -> None:
    client = TestClient(
        build_test_app()
    )

    response = client.get(
        "/api/v1/market-data/status"
    )

    assert response.status_code == 200


def test_authenticated_route_rejects_missing_token() -> None:
    client = TestClient(
        build_test_app()
    )

    response = client.get(
        "/api/v1/analytics"
    )

    assert response.status_code == 401

    assert response.headers[
        "www-authenticate"
    ] == "Bearer"


def test_authenticated_route_accepts_principal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    principal = SimpleNamespace(
        subject="user-1",
        claims={
            "role": "viewer",
        },
    )

    monkeypatch.setattr(
        route_protection,
        "authenticate_bearer_credentials",
        lambda credentials: principal,
    )

    async def load_identity_state(
        user_id: str,
    ) -> dict[str, object]:
        assert user_id == 'user-1'

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
        build_test_app()
    )

    response = client.get(
        "/api/v1/analytics",
        headers={
            "Authorization": (
                "Bearer access-token"
            ),
        },
    )

    assert response.status_code == 200


def test_admin_route_rejects_non_admin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    principal = SimpleNamespace(
        subject="user-1",
        claims={
            "role": "viewer",
        },
    )

    monkeypatch.setattr(
        route_protection,
        "authenticate_bearer_credentials",
        lambda credentials: principal,
    )

    async def load_identity_state(
        user_id: str,
    ) -> dict[str, object]:
        assert user_id == 'user-1'

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
        build_test_app()
    )

    response = client.post(
        "/api/v1/admin/backup",
        headers={
            "Authorization": (
                "Bearer access-token"
            ),
        },
    )

    assert response.status_code == 403


def test_admin_route_accepts_server_claim(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    principal = SimpleNamespace(
        subject="admin-1",
        claims={
            "role": "admin",
        },
    )

    monkeypatch.setattr(
        route_protection,
        "authenticate_bearer_credentials",
        lambda credentials: principal,
    )

    async def load_identity_state(
        user_id: str,
    ) -> dict[str, object]:
        assert user_id == 'admin-1'

        return {
            "is_active": True,
            "status": "active",
            "role": 'admin',
            "must_change_password": False,
        }

    monkeypatch.setattr(
        route_protection,
        "_load_identity_authorization_state",
        load_identity_state,
    )

    client = TestClient(
        build_test_app()
    )

    response = client.post(
        "/api/v1/admin/backup",
        headers={
            "Authorization": (
                "Bearer access-token"
            ),
        },
    )

    assert response.status_code == 200


def test_unknown_route_preserves_not_found() -> None:
    client = TestClient(
        build_test_app()
    )

    response = client.get(
        "/not-a-real-route"
    )

    assert response.status_code == 404


def test_refresh_token_validation_failure_is_unauthorized(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def reject(
        credentials,
    ):
        raise RuntimeError(
            "Refresh token is not an access token"
        )

    monkeypatch.setattr(
        route_protection,
        "authenticate_bearer_credentials",
        reject,
    )

    client = TestClient(
        build_test_app()
    )

    response = client.get(
        "/api/v1/analytics",
        headers={
            "Authorization": (
                "Bearer refresh-token"
            ),
        },
    )

    assert response.status_code == 401
