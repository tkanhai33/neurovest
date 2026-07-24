from __future__ import annotations

from types import SimpleNamespace

import pytest

from fastapi import HTTPException

from fastapi.security import (
    HTTPAuthorizationCredentials,
)

from backend.app.stacks.identity_auth import (
    api_dependencies,
)


@pytest.mark.asyncio
async def test_missing_bearer_credentials_fail_closed() -> None:
    with pytest.raises(
        HTTPException
    ) as captured:
        await (
            api_dependencies
            .require_authenticated_principal(
                None
            )
        )

    assert captured.value.status_code == 401

    assert captured.value.headers == {
        "WWW-Authenticate": "Bearer",
    }


@pytest.mark.asyncio
async def test_valid_principal_is_returned(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    principal = SimpleNamespace(
        subject="user-1",
        claims={
            "role": "viewer",
        },
    )

    monkeypatch.setattr(
        api_dependencies,
        "authenticate_bearer_credentials",
        lambda credentials: principal,
    )

    result = await (
        api_dependencies
        .require_authenticated_principal(
            HTTPAuthorizationCredentials(
                scheme="Bearer",
                credentials="access-token",
            )
        )
    )

    assert result is principal


@pytest.mark.asyncio
async def test_invalid_credentials_are_generic(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail(
        credentials,
    ):
        raise RuntimeError(
            "internal token validation detail"
        )

    monkeypatch.setattr(
        api_dependencies,
        "authenticate_bearer_credentials",
        fail,
    )

    with pytest.raises(
        HTTPException
    ) as captured:
        await (
            api_dependencies
            .require_authenticated_principal(
                HTTPAuthorizationCredentials(
                    scheme="Bearer",
                    credentials="bad-token",
                )
            )
        )

    assert captured.value.status_code == 401

    assert captured.value.detail == (
        "Invalid authentication credentials"
    )

    assert captured.value.headers == {
        "WWW-Authenticate": "Bearer",
    }
