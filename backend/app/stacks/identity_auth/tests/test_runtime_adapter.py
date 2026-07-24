from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from backend.app.stacks.identity_auth.errors import (
    MissingSecretError,
)

from backend.app.stacks.identity_auth.login_service import (
    LoginService,
)

from backend.app.stacks.identity_auth.registration_service import (
    RegistrationService,
)

from backend.app.stacks.identity_auth.runtime_adapter import (
    EnvironmentJwtTokenIssuer,
    build_authentication_runtime,
)


class FakeSession:
    def __init__(self) -> None:
        self.commit = AsyncMock()
        self.rollback = AsyncMock()

    def add(
        self,
        value,
    ) -> None:
        raise AssertionError(
            "Runtime construction must not add records"
        )

    async def flush(
        self,
    ) -> None:
        raise AssertionError(
            "Runtime construction must not flush records"
        )

    async def execute(
        self,
        statement,
    ):
        raise AssertionError(
            "Runtime construction must not query records"
        )


def install_controlled_secret(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "NEUROVEST_JWT_SECRET",
        (
            "controlled-nonproduction-"
            "jwt-secret-"
            "0123456789abcdef0123456789abcdef"
        ),
    )


def test_runtime_construction_is_non_mutating(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_controlled_secret(
        monkeypatch
    )

    session = FakeSession()

    registration, login = (
        build_authentication_runtime(
            session
        )
    )

    assert isinstance(
        registration,
        RegistrationService,
    )

    assert isinstance(
        login,
        LoginService,
    )

    session.commit.assert_not_awaited()
    session.rollback.assert_not_awaited()


def test_runtime_fails_closed_without_secret(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(
        "NEUROVEST_JWT_SECRET",
        raising=False,
    )

    with pytest.raises(
        MissingSecretError
    ):
        build_authentication_runtime(
            FakeSession()
        )


@pytest.mark.asyncio
async def test_real_access_and_refresh_token_paths(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_controlled_secret(
        monkeypatch
    )

    issuer = EnvironmentJwtTokenIssuer()

    access = await issuer.issue_access_token(
        subject="qualification-user"
    )

    refresh = await issuer.issue_refresh_token(
        subject="qualification-user"
    )

    assert access.token
    assert refresh.token

    assert access.token != refresh.token

    assert access.token_id
    assert refresh.token_id

    assert (
        access.token_id
        != refresh.token_id
    )

    assert (
        access.expires_at
        > access.issued_at
    )

    assert (
        refresh.expires_at
        > refresh.issued_at
    )
