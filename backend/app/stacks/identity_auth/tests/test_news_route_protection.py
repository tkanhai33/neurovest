from __future__ import annotations

from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.stacks.identity_auth import (
    route_protection,
)
from backend.app.stacks.identity_auth.route_protection import (
    resolve_route_policy,
)


def test_news_route_is_authenticated() -> None:
    assert (
        resolve_route_policy(
            "GET",
            "/api/v1/news",
        )
        == "AUTHENTICATED"
    )


def test_anonymous_news_request_is_denied() -> None:
    app = FastAPI()
    app.middleware("http")(
        route_protection.enforce_route_policy
    )

    @app.get("/api/v1/news")
    async def policy_stub():
        return {"status": "ok"}

    principal_box: list[object | None] = [None]

    async def fake_authenticate_request(_request):
        return principal_box[0]

    async def fake_identity_state(_subject: str):
        return {
            "is_active": True,
            "status": "active",
            "must_change_password": False,
        }

    async def no_trace(**_kwargs):
        return None

    original_authenticate = (
        route_protection._authenticate_request
    )
    original_identity_state = (
        route_protection._load_identity_authorization_state
    )
    original_emit = route_protection.emit_runtime_step

    route_protection._authenticate_request = (
        fake_authenticate_request
    )
    route_protection._load_identity_authorization_state = (
        fake_identity_state
    )
    route_protection.emit_runtime_step = no_trace

    try:
        with TestClient(app) as client:
            anonymous = client.get("/api/v1/news")

            principal_box[0] = SimpleNamespace(
                subject="news-policy-qualification-user",
                claims={"role": "user"},
            )

            authenticated = client.get("/api/v1/news")
    finally:
        route_protection._authenticate_request = (
            original_authenticate
        )
        route_protection._load_identity_authorization_state = (
            original_identity_state
        )
        route_protection.emit_runtime_step = original_emit

    assert anonymous.status_code == 401
    assert authenticated.status_code == 200
