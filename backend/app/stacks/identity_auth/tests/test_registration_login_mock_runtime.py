from __future__ import annotations

import pytest

from backend.app.stacks.identity_auth.mock_runtime import (
    MockAuthenticationRuntime,
    mock_hash_refresh_token,
)

from backend.app.stacks.identity_auth.service_contracts import (
    AuthenticationRejectedError,
    LoginCommand,
    RegistrationCommand,
    RegistrationRejectedError,
)


@pytest.mark.asyncio
async def test_complete_mock_registration_and_login_flow() -> None:
    runtime = MockAuthenticationRuntime()

    registered = await runtime.registration.register(
        RegistrationCommand(
            email=" MockUser@Example.COM ",
            password="correct-password",
        )
    )

    assert registered.email_normalized == (
        "mockuser@example.com"
    )

    assert runtime.registration_transaction.commit_count == 1
    assert runtime.registration_transaction.rollback_count == 0

    result = await runtime.login.login(
        LoginCommand(
            email="mockuser@example.com",
            password="correct-password",
        )
    )

    assert result.access_token.startswith(
        "mock-access-"
    )

    assert result.refresh_token.startswith(
        "mock-refresh-"
    )

    assert result.access_token != result.refresh_token

    assert runtime.login_transaction.commit_count == 1
    assert runtime.login_transaction.rollback_count == 0

    assert len(
        runtime.refresh_sessions.sessions
    ) == 1

    session = runtime.refresh_sessions.sessions[
        0
    ]

    assert session.user_id == registered.user_id

    assert session.token_hash == (
        mock_hash_refresh_token(
            result.refresh_token
        )
    )

    assert result.refresh_token not in (
        session.token_hash
    )


@pytest.mark.asyncio
async def test_duplicate_registration_rolls_back() -> None:
    runtime = MockAuthenticationRuntime()

    command = RegistrationCommand(
        email="user@example.com",
        password="correct-password",
    )

    await runtime.registration.register(
        command
    )

    with pytest.raises(
        RegistrationRejectedError,
        match="Registration could not be completed",
    ):
        await runtime.registration.register(
            command
        )

    assert runtime.registration_transaction.commit_count == 1
    assert runtime.registration_transaction.rollback_count == 1

    assert len(
        runtime.users.users_by_email
    ) == 1


@pytest.mark.asyncio
async def test_unknown_and_wrong_password_share_error() -> None:
    runtime = MockAuthenticationRuntime()

    await runtime.registration.register(
        RegistrationCommand(
            email="user@example.com",
            password="correct-password",
        )
    )

    with pytest.raises(
        AuthenticationRejectedError
    ) as unknown_error:
        await runtime.login.login(
            LoginCommand(
                email="missing@example.com",
                password="wrong-password",
            )
        )

    with pytest.raises(
        AuthenticationRejectedError
    ) as password_error:
        await runtime.login.login(
            LoginCommand(
                email="user@example.com",
                password="wrong-password",
            )
        )

    assert str(
        unknown_error.value
    ) == str(
        password_error.value
    ) == "Authentication failed"

    assert runtime.token_issuer.access_issued == 0
    assert runtime.token_issuer.refresh_issued == 0

    assert len(
        runtime.refresh_sessions.sessions
    ) == 0


@pytest.mark.asyncio
async def test_disabled_account_rejected_before_token_issuance() -> None:
    runtime = MockAuthenticationRuntime()

    registered = await runtime.registration.register(
        RegistrationCommand(
            email="user@example.com",
            password="correct-password",
        )
    )

    user = runtime.users.users_by_email[
        registered.email_normalized
    ]

    user.is_active = False

    with pytest.raises(
        AuthenticationRejectedError,
        match="Authentication failed",
    ):
        await runtime.login.login(
            LoginCommand(
                email="user@example.com",
                password="correct-password",
            )
        )

    assert runtime.token_issuer.access_issued == 0
    assert runtime.token_issuer.refresh_issued == 0

    assert len(
        runtime.refresh_sessions.sessions
    ) == 0


@pytest.mark.asyncio
async def test_access_token_failure_rolls_back() -> None:
    runtime = MockAuthenticationRuntime()

    await runtime.registration.register(
        RegistrationCommand(
            email="user@example.com",
            password="correct-password",
        )
    )

    runtime.token_issuer.fail_access = True

    with pytest.raises(
        AuthenticationRejectedError,
        match="Authentication failed",
    ):
        await runtime.login.login(
            LoginCommand(
                email="user@example.com",
                password="correct-password",
            )
        )

    assert runtime.login_transaction.commit_count == 0
    assert runtime.login_transaction.rollback_count == 1

    assert len(
        runtime.refresh_sessions.sessions
    ) == 0


@pytest.mark.asyncio
async def test_refresh_token_failure_rolls_back() -> None:
    runtime = MockAuthenticationRuntime()

    await runtime.registration.register(
        RegistrationCommand(
            email="user@example.com",
            password="correct-password",
        )
    )

    runtime.token_issuer.fail_refresh = True

    with pytest.raises(
        AuthenticationRejectedError,
        match="Authentication failed",
    ):
        await runtime.login.login(
            LoginCommand(
                email="user@example.com",
                password="correct-password",
            )
        )

    assert runtime.login_transaction.commit_count == 0
    assert runtime.login_transaction.rollback_count == 1

    assert len(
        runtime.refresh_sessions.sessions
    ) == 0


@pytest.mark.asyncio
async def test_refresh_session_failure_rolls_back() -> None:
    runtime = MockAuthenticationRuntime()

    await runtime.registration.register(
        RegistrationCommand(
            email="user@example.com",
            password="correct-password",
        )
    )

    runtime.refresh_sessions.fail_create = True

    with pytest.raises(
        AuthenticationRejectedError,
        match="Authentication failed",
    ):
        await runtime.login.login(
            LoginCommand(
                email="user@example.com",
                password="correct-password",
            )
        )

    assert runtime.login_transaction.commit_count == 0
    assert runtime.login_transaction.rollback_count == 1

    assert len(
        runtime.refresh_sessions.sessions
    ) == 0


@pytest.mark.asyncio
async def test_registration_commit_failure_fails_closed() -> None:
    runtime = MockAuthenticationRuntime()

    runtime.registration_transaction.fail_commit = True

    with pytest.raises(
        RegistrationRejectedError,
        match="Registration could not be completed",
    ):
        await runtime.registration.register(
            RegistrationCommand(
                email="user@example.com",
                password="correct-password",
            )
        )

    assert runtime.registration_transaction.commit_count == 0
    assert runtime.registration_transaction.rollback_count == 1


@pytest.mark.asyncio
async def test_login_commit_failure_fails_closed() -> None:
    runtime = MockAuthenticationRuntime()

    await runtime.registration.register(
        RegistrationCommand(
            email="user@example.com",
            password="correct-password",
        )
    )

    runtime.login_transaction.fail_commit = True

    with pytest.raises(
        AuthenticationRejectedError,
        match="Authentication failed",
    ):
        await runtime.login.login(
            LoginCommand(
                email="user@example.com",
                password="correct-password",
            )
        )

    assert runtime.login_transaction.commit_count == 0
    assert runtime.login_transaction.rollback_count == 1
