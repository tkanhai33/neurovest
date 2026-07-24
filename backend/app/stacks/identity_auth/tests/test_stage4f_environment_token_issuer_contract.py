from __future__ import annotations

import inspect

import pytest

from backend.app.stacks.identity_auth.runtime_adapter import (
    EnvironmentJwtTokenIssuer,
)

from backend.app.stacks.identity_auth.tokens import (
    validate_access_token,
    validate_refresh_token,
)


TEST_SECRET = (
    "stage4f-g9-environment-issuer-"
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


def test_environment_issuer_signatures_accept_extra_claims() -> None:
    for name in (
        "issue_access_token",
        "issue_refresh_token",
    ):
        signature = inspect.signature(
            getattr(
                EnvironmentJwtTokenIssuer,
                name,
            )
        )

        assert (
            "extra_claims"
            in signature.parameters
        )


@pytest.mark.asyncio
async def test_environment_access_issuer_forwards_claims() -> None:
    issuer = EnvironmentJwtTokenIssuer()

    issued = await issuer.issue_access_token(
        subject="stage4f-owner",
        extra_claims={
            "authorization_role": "developer",
            "subscription_tier": "internal",
        },
    )

    claims = validate_access_token(
        issued.token
    )

    assert (
        claims.extra["authorization_role"]
        == "developer"
    )

    assert (
        claims.extra["subscription_tier"]
        == "internal"
    )


@pytest.mark.asyncio
async def test_environment_refresh_issuer_forwards_claims() -> None:
    issuer = EnvironmentJwtTokenIssuer()

    issued = await issuer.issue_refresh_token(
        subject="stage4f-owner",
        extra_claims={
            "authorization_role": "developer",
            "subscription_tier": "internal",
        },
    )

    claims = validate_refresh_token(
        issued.token
    )

    assert (
        claims.extra["authorization_role"]
        == "developer"
    )

    assert (
        claims.extra["subscription_tier"]
        == "internal"
    )
