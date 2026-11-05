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
        terms_version="neurovest-beta-terms-2026-10-09-v1",
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

    assert session.add.call_count == 2
    assert session.add.call_args_list[0].args[0] is user

    acceptance = session.add.call_args_list[1].args[0]
    assert acceptance.user_id == user.id
    assert acceptance.document_version == "neurovest-beta-terms-2026-10-09-v1"
    assert session.flush.await_count == 2


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
