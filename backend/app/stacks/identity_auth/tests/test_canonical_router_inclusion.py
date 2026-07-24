from __future__ import annotations

import ast
from datetime import (
    UTC,
    datetime,
    timedelta,
)
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.stacks.identity_auth.api_dependencies import (
    get_login_api_service,
    get_registration_api_service,
)

from backend.app.stacks.identity_auth.api_router import (
    router as auth_router,
)

from backend.app.stacks.identity_auth.service_contracts import (
    AuthenticationTokenPair,
    LoginCommand,
    RegisteredIdentity,
    RegistrationCommand,
)


class QualificationRegistrationService:
    async def register(
        self,
        command: RegistrationCommand,
    ) -> RegisteredIdentity:
        return RegisteredIdentity(
            user_id="canonical-qualification-user",
            email_normalized=command.email.lower(),
            status="active",
        )


class QualificationLoginService:
    async def login(
        self,
        command: LoginCommand,
    ) -> AuthenticationTokenPair:
        issued_at = datetime.now(
            UTC
        )

        return AuthenticationTokenPair(
            access_token="qualification-access",
            refresh_token="qualification-refresh",
            token_type="bearer",
            access_expires_at=(
                issued_at
                + timedelta(
                    minutes=15
                )
            ),
            refresh_expires_at=(
                issued_at
                + timedelta(
                    days=7
                )
            ),
        )


def test_canonical_source_includes_auth_router_once() -> None:
    source = Path(
        "backend/app/main.py"
    ).read_text(
        encoding="utf-8"
    )

    assert source.count(
        (
            "from backend.app.stacks.identity_auth."
            "api_router import router as auth_router"
        )
    ) == 1

    assert source.count(
        "app.include_router(auth_router)"
    ) == 1

    ast.parse(
        source,
        filename="backend/app/main.py",
    )


def test_auth_router_has_complete_session_lifecycle() -> None:
    routes = {
        (
            method,
            route.path,
        )
        for route in auth_router.routes
        for method in route.methods
    }

    required_routes = {
        (
            "POST",
            "/auth/register",
        ),
        (
            "POST",
            "/auth/login",
        ),
        (
            "POST",
            "/auth/refresh",
        ),
        (
            "POST",
            "/auth/logout",
        ),
        (
            "POST",
            "/auth/logout-all",
        ),
    }

    assert required_routes <= routes


def test_controlled_local_registration_and_login() -> None:
    app = FastAPI()

    app.include_router(
        auth_router
    )

    registration_service = (
        QualificationRegistrationService()
    )

    login_service = (
        QualificationLoginService()
    )

    app.dependency_overrides[
        get_registration_api_service
    ] = lambda: registration_service

    app.dependency_overrides[
        get_login_api_service
    ] = lambda: login_service

    client = TestClient(
        app
    )

    registration = client.post(
        "/auth/register",
        json={
            "email": "qualification@example.com",
            "password": "qualification-password-123",
        },
    )

    assert registration.status_code == 201

    login = client.post(
        "/auth/login",
        json={
            "email": "qualification@example.com",
            "password": "qualification-password-123",
        },
    )

    assert login.status_code == 200

    assert login.json() == {
        "token_type": "bearer",
        "access_token": "qualification-access",
        "refresh_token": "qualification-refresh",
    }
