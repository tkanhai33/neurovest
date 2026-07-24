from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from backend.app.stacks.identity_auth.models import (
    IdentityUser,
)

from backend.app.stacks.identity_auth.repositories import (
    IdentityUserRepository,
)


@pytest.mark.asyncio
async def test_user_repository_normalizes_email() -> None:
    session = Mock()

    session.add = Mock()

    session.flush = AsyncMock()

    repository = IdentityUserRepository(
        session
    )

    user = await repository.create(
        email="  User@Example.COM ",
        password_hash="scrypt$test",
    )

    assert isinstance(
        user,
        IdentityUser,
    )

    assert user.email_normalized == (
        "user@example.com"
    )

    assert user.password_hash == (
        "scrypt$test"
    )

    session.add.assert_called_once_with(
        user
    )

    session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_user_repository_rejects_empty_hash() -> None:
    repository = IdentityUserRepository(
        Mock()
    )

    with pytest.raises(
        ValueError
    ):
        await repository.create(
            email="user@example.com",
            password_hash="",
        )
