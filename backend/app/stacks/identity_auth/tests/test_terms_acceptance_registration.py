from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from backend.app.stacks.identity_auth.registration_service import (
    RegistrationService,
)
from backend.app.stacks.identity_auth.service_contracts import (
    RegistrationCommand,
    RegistrationRejectedError,
)


@pytest.mark.asyncio
async def test_registration_rejects_unaccepted_terms() -> None:
    repository = Mock()
    repository.get_by_email = AsyncMock(
        return_value=None
    )
    repository.create = AsyncMock()

    commit = AsyncMock()
    rollback = AsyncMock()

    service = RegistrationService(
        user_repository=repository,
        hash_password=lambda value: "hash:" + value,
        commit=commit,
        rollback=rollback,
    )

    with pytest.raises(
        RegistrationRejectedError,
        match="Registration could not be completed",
    ):
        await service.register(
            RegistrationCommand(
                email="user@example.com",
                password="long-enough-password",
                terms_accepted=False,
                terms_version="neurovest-beta-terms-2026-10-09-v1",
            )
        )

    repository.create.assert_not_awaited()
    commit.assert_not_awaited()
    rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_registration_passes_document_version_to_repository() -> None:
    user = Mock(
        id="qualification-user",
        email_normalized="user@example.com",
        status="active",
    )

    repository = Mock()
    repository.get_by_email = AsyncMock(
        return_value=None
    )
    repository.create = AsyncMock(
        return_value=user
    )

    commit = AsyncMock()
    rollback = AsyncMock()

    service = RegistrationService(
        user_repository=repository,
        hash_password=lambda value: "hash:" + value,
        commit=commit,
        rollback=rollback,
    )

    await service.register(
        RegistrationCommand(
            email="user@example.com",
            password="long-enough-password",
            terms_accepted=True,
            terms_version="neurovest-beta-terms-2026-10-09-v1",
        )
    )

    repository.create.assert_awaited_once_with(
        email="user@example.com",
        password_hash="hash:long-enough-password",
        display_name=None,
        terms_version="neurovest-beta-terms-2026-10-09-v1",
    )
    commit.assert_awaited_once()
    rollback.assert_not_awaited()
