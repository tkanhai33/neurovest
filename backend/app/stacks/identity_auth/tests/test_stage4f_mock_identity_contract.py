from __future__ import annotations

import inspect

import pytest

from backend.app.stacks.identity_auth.mock_runtime import (
    MockAuthenticationRuntime,
    MockServiceTokenIssuer,
)

from backend.app.stacks.identity_auth.service_contracts import (
    LoginCommand,
    RegistrationCommand,
)


@pytest.mark.asyncio
async def test_mock_access_issuer_accepts_and_records_claims() -> None:
    issuer = MockServiceTokenIssuer()

    issued = await issuer.issue_access_token(
        subject="stage4f-user",
        extra_claims={
            "authorization_role": "developer",
            "subscription_tier": "internal",
        },
    )

    assert issued.token
    assert issued.token_id

    assert issuer.last_access_extra_claims == {
        "authorization_role": "developer",
        "subscription_tier": "internal",
    }


@pytest.mark.asyncio
async def test_mock_refresh_issuer_accepts_and_records_claims() -> None:
    issuer = MockServiceTokenIssuer()

    issued = await issuer.issue_refresh_token(
        subject="stage4f-user",
        extra_claims={
            "authorization_role": "admin",
            "subscription_tier": "enterprise",
        },
    )

    assert issued.token
    assert issued.token_id

    assert issuer.last_refresh_extra_claims == {
        "authorization_role": "admin",
        "subscription_tier": "enterprise",
    }


def test_mock_issuer_signatures_match_claim_contract() -> None:
    for method_name in (
        "issue_access_token",
        "issue_refresh_token",
    ):
        method = getattr(
            MockServiceTokenIssuer,
            method_name,
        )

        signature = inspect.signature(
            method
        )

        assert "extra_claims" in signature.parameters

        parameter = signature.parameters[
            "extra_claims"
        ]

        assert parameter.default is None


@pytest.mark.asyncio
async def test_mock_registration_result_remains_registration_contract() -> None:
    runtime = MockAuthenticationRuntime()

    registered = await runtime.registration.register(
        RegistrationCommand(
            email="stage4f-contract@example.com",
            password="correct-password",
        )
    )

    assert registered is not None
    assert registered.user_id
    assert registered.email_normalized

    assert not hasattr(
        registered,
        "role",
    )

    assert not hasattr(
        registered,
        "subscription_tier",
    )


@pytest.mark.asyncio
async def test_mock_registration_login_flow_accepts_claim_propagation() -> None:
    runtime = MockAuthenticationRuntime()

    await runtime.registration.register(
        RegistrationCommand(
            email="stage4f-login@example.com",
            password="correct-password",
        )
    )

    result = await runtime.login.login(
        LoginCommand(
            email="stage4f-login@example.com",
            password="correct-password",
        )
    )

    assert result.access_token
    assert result.refresh_token

    assert (
        result.access_token
        != result.refresh_token
    )
