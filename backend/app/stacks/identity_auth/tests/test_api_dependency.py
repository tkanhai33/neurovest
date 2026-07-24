from __future__ import annotations

import pytest
from fastapi import HTTPException
from fastapi.security import (
    HTTPAuthorizationCredentials,
)

from backend.app.stacks.identity_auth.dependencies import (
    authenticate_bearer_credentials,
)

from backend.app.stacks.identity_auth.tokens import (
    issue_access_token,
    issue_refresh_token,
)


TEST_SECRET = (
    "test-only-secret-material-"
    "0123456789abcdef"
)


@pytest.fixture(autouse=True)
def jwt_secret(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "NEUROVEST_JWT_SECRET",
        TEST_SECRET,
    )


def test_missing_bearer_credentials_are_unauthorized() -> None:
    with pytest.raises(
        HTTPException
    ) as captured:
        authenticate_bearer_credentials(
            None
        )

    assert captured.value.status_code == 401


def test_wrong_scheme_is_unauthorized() -> None:
    credentials = HTTPAuthorizationCredentials(
        scheme="Basic",
        credentials="value",
    )

    with pytest.raises(
        HTTPException
    ) as captured:
        authenticate_bearer_credentials(
            credentials
        )

    assert captured.value.status_code == 401


def test_valid_access_token_returns_principal() -> None:
    token = issue_access_token(
        "user-1",
        extra_claims={
            "role": "viewer",
        },
    )

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token,
    )

    principal = authenticate_bearer_credentials(
        credentials
    )

    assert principal.subject == "user-1"
    assert principal.claims[
        "role"
    ] == "viewer"


def test_refresh_token_is_rejected_by_api_dependency() -> None:
    token = issue_refresh_token(
        "user-1"
    )

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token,
    )

    with pytest.raises(
        HTTPException
    ) as captured:
        authenticate_bearer_credentials(
            credentials
        )

    assert captured.value.status_code == 401


def test_malformed_token_is_unauthorized() -> None:
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="invalid-token",
    )

    with pytest.raises(
        HTTPException
    ) as captured:
        authenticate_bearer_credentials(
            credentials
        )

    assert captured.value.status_code == 401
