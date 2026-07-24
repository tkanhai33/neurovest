from __future__ import annotations

from datetime import (
    UTC,
    datetime,
    timedelta,
)

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.stacks.identity_auth.api_dependencies import (
    get_login_api_service,
    get_registration_api_service,
)

from backend.app.stacks.identity_auth.api_router import (
    router,
)

from backend.app.stacks.identity_auth.service_contracts import (
    AuthenticationTokenPair,
    LoginCommand,
    RegisteredIdentity,
    RegistrationCommand,
)


class FakeRegistrationService:
    def __init__(
        self,
        *,
        failure: Exception | None = None,
    ) -> None:
        self.failure = failure
        self.command = None

    async def register(
        self,
        command: RegistrationCommand,
    ) -> RegisteredIdentity:
        self.command = command

        if self.failure is not None:
            raise self.failure

        return RegisteredIdentity(
            user_id="qualification-user",
            email_normalized=command.email.lower(),
            status="active",
        )


class FakeLoginService:
    def __init__(
        self,
        *,
        failure: Exception | None = None,
    ) -> None:
        self.failure = failure
        self.command = None

    async def login(
        self,
        command: LoginCommand,
    ) -> AuthenticationTokenPair:
        self.command = command

        if self.failure is not None:
            raise self.failure

        issued_at = datetime.now(
            UTC
        )

        return AuthenticationTokenPair(
            access_token="access-token",
            refresh_token="refresh-token",
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


def build_test_app(
    registration_service=None,
    login_service=None,
) -> FastAPI:
    app = FastAPI()

    app.include_router(
        router
    )

    if registration_service is not None:
        app.dependency_overrides[
            get_registration_api_service
        ] = lambda: registration_service

    if login_service is not None:
        app.dependency_overrides[
            get_login_api_service
        ] = lambda: login_service

    return app


def test_registration_contract() -> None:
    service = FakeRegistrationService()

    client = TestClient(
        build_test_app(
            registration_service=service
        )
    )

    response = client.post(
        "/auth/register",
        json={
            "email": "user@example.com",
            "password": "safe-password-123",
        },
    )

    assert response.status_code == 201

    assert response.json() == {
        "status": "registered",
    }

    assert service.command == RegistrationCommand(
        email="user@example.com",
        password="safe-password-123",
    )


def test_registration_failure_is_generic() -> None:
    service = FakeRegistrationService(
        failure=RuntimeError(
            "internal registration detail"
        )
    )

    client = TestClient(
        build_test_app(
            registration_service=service
        )
    )

    response = client.post(
        "/auth/register",
        json={
            "email": "user@example.com",
            "password": "safe-password-123",
        },
    )

    assert response.status_code == 400

    assert response.json() == {
        "detail": (
            "Registration could not be completed"
        ),
    }

    assert (
        "internal registration detail"
        not in response.text
    )


def test_login_contract() -> None:
    service = FakeLoginService()

    client = TestClient(
        build_test_app(
            login_service=service
        )
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "user@example.com",
            "password": "safe-password-123",
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "token_type": "bearer",
        "access_token": "access-token",
        "refresh_token": "refresh-token",
    }

    assert service.command == LoginCommand(
        email="user@example.com",
        password="safe-password-123",
    )


def test_login_failure_is_generic() -> None:
    service = FakeLoginService(
        failure=RuntimeError(
            "unknown user or wrong password"
        )
    )

    client = TestClient(
        build_test_app(
            login_service=service
        )
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "user@example.com",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401

    assert response.json() == {
        "detail": (
            "Invalid authentication credentials"
        ),
    }

    assert response.headers[
        "www-authenticate"
    ] == "Bearer"

    assert (
        "unknown user"
        not in response.text
    )


def test_router_is_activated_in_canonical_app() -> None:
    from pathlib import Path

    main_source = Path(
        "backend/app/main.py"
    ).read_text(
        encoding="utf-8"
    )

    assert main_source.count(
        (
            "from backend.app.stacks.identity_auth."
            "api_router import router as auth_router"
        )
    ) == 1

    assert main_source.count(
        "app.include_router(auth_router)"
    ) == 1
