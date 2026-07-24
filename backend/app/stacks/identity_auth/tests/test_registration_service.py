from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import (
    AsyncMock,
    Mock,
)

import pytest

from backend.app.stacks.identity_auth.registration_service import (
    RegistrationService,
)

from backend.app.stacks.identity_auth.service_contracts import (
    RegistrationCommand,
    RegistrationRejectedError,
)


def build_service(
    *,
    existing=None,
    created=None,
    hash_result: str = "scrypt$derived",
):
    repository = Mock()

    repository.get_by_email = AsyncMock(
        return_value=existing
    )

    repository.create = AsyncMock(
        return_value=(
            created
            or SimpleNamespace(
                id="user-1",
                email_normalized=(
                    "user@example.com"
                ),
                status="active",
            )
        )
    )

    hash_password = Mock(
        return_value=hash_result
    )

    commit = AsyncMock()
    rollback = AsyncMock()

    service = RegistrationService(
        user_repository=repository,
        hash_password=hash_password,
        commit=commit,
        rollback=rollback,
    )

    return (
        service,
        repository,
        hash_password,
        commit,
        rollback,
    )


@pytest.mark.asyncio
async def test_registration_normalizes_and_hashes_password() -> None:
    (
        service,
        repository,
        hash_password,
        commit,
        rollback,
    ) = build_service()

    result = await service.register(
        RegistrationCommand(
            email=" User@Example.COM ",
            password="test-password",
        )
    )

    repository.get_by_email.assert_awaited_once_with(
        "user@example.com"
    )

    hash_password.assert_called_once_with(
        "test-password"
    )

    repository.create.assert_awaited_once_with(
        email="user@example.com",
        password_hash="scrypt$derived",
        display_name=None,
    )

    commit.assert_awaited_once()
    rollback.assert_not_awaited()

    assert result.user_id == "user-1"
    assert result.email_normalized == (
        "user@example.com"
    )

    assert not hasattr(
        result,
        "access_token",
    )

    assert not hasattr(
        result,
        "refresh_token",
    )


@pytest.mark.asyncio
async def test_duplicate_registration_fails_generically() -> None:
    service, _, hash_password, commit, rollback = (
        build_service(
            existing=object()
        )
    )

    with pytest.raises(
        RegistrationRejectedError,
        match="Registration could not be completed",
    ):
        await service.register(
            RegistrationCommand(
                email="user@example.com",
                password="test-password",
            )
        )

    hash_password.assert_not_called()
    commit.assert_not_awaited()
    rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_registration_hash_failure_rolls_back() -> None:
    service, _, hash_password, commit, rollback = (
        build_service()
    )

    hash_password.side_effect = RuntimeError(
        "hash failure"
    )

    with pytest.raises(
        RegistrationRejectedError,
        match="Registration could not be completed",
    ):
        await service.register(
            RegistrationCommand(
                email="user@example.com",
                password="test-password",
            )
        )

    commit.assert_not_awaited()
    rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_empty_password_fails_closed() -> None:
    service, repository, _, commit, rollback = (
        build_service()
    )

    with pytest.raises(
        RegistrationRejectedError,
        match="Registration could not be completed",
    ):
        await service.register(
            RegistrationCommand(
                email="user@example.com",
                password="",
            )
        )

    repository.create.assert_not_awaited()
    commit.assert_not_awaited()
    rollback.assert_awaited_once()
