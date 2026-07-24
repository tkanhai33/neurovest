from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

import pytest

from backend.app.stacks.identity_auth.password_change_service import (
    PasswordChangeRejectedError,
    RequiredPasswordChangeService,
    validate_replacement_password,
)

from backend.app.stacks.identity_auth.passwords import (
    hash_password,
    verify_password,
)


@dataclass
class FakeUser:
    id: str
    password_hash: str
    is_active: bool = True
    status: str = "active"
    role: str = "owner"
    must_change_password: bool = True


class FakeUserRepository:
    def __init__(
        self,
        user: FakeUser,
    ) -> None:
        self.user = user

    async def get_by_id(
        self,
        user_id: str,
    ):
        return (
            self.user
            if user_id == self.user.id
            else None
        )

    async def update_password_hash(
        self,
        user,
        *,
        password_hash: str,
    ):
        user.password_hash = password_hash
        return user

    async def update_identity_security_state(
        self,
        user,
        *,
        role=None,
        must_change_password=None,
    ):
        if role is not None:
            user.role = role

        if must_change_password is not None:
            user.must_change_password = (
                must_change_password
            )

        return user


class FakeRefreshRepository:
    def __init__(self) -> None:
        self.revoked = False

    async def revoke_all_for_user(
        self,
        user_id: str,
        *,
        revoked_at: datetime,
    ) -> int:
        self.revoked = True
        return 2


@pytest.mark.parametrize(
    "password",
    (
        "short",
        "alllowercase123!",
        "ALLUPPERCASE123!",
        "NoNumbersHere!",
        "NoSymbolsHere123",
    ),
)
def test_replacement_password_policy_rejects_weak_values(
    password: str,
) -> None:
    with pytest.raises(
        PasswordChangeRejectedError
    ):
        validate_replacement_password(
            password
        )


def test_replacement_password_policy_accepts_strong_value() -> None:
    validate_replacement_password(
        "NeuroVest-Strong!2026"
    )


@pytest.mark.asyncio
async def test_required_password_change_updates_hash_and_revokes_sessions() -> None:
    user = FakeUser(
        id="user-1",
        password_hash=hash_password(
            "pass123"
        ),
    )

    users = FakeUserRepository(
        user
    )

    sessions = FakeRefreshRepository()

    committed = False
    rolled_back = False

    async def commit() -> None:
        nonlocal committed
        committed = True

    async def rollback() -> None:
        nonlocal rolled_back
        rolled_back = True

    service = RequiredPasswordChangeService(
        user_repository=users,
        refresh_repository=sessions,
        commit=commit,
        rollback=rollback,
    )

    result = await service.replace_required_password(
        user_id=user.id,
        current_password="pass123",
        new_password="NeuroVest-Strong!2026",
    )

    assert result.revoked_sessions == 2
    assert user.must_change_password is False
    assert sessions.revoked is True
    assert committed is True
    assert rolled_back is False

    assert verify_password(
        "NeuroVest-Strong!2026",
        user.password_hash,
    )

    assert not verify_password(
        "pass123",
        user.password_hash,
    )


@pytest.mark.asyncio
async def test_wrong_temporary_password_fails_closed() -> None:
    user = FakeUser(
        id="user-1",
        password_hash=hash_password(
            "pass123"
        ),
    )

    service = RequiredPasswordChangeService(
        user_repository=FakeUserRepository(
            user
        ),
        refresh_repository=FakeRefreshRepository(),
        commit=lambda: None,
        rollback=lambda: None,
    )

    async def commit() -> None:
        return None

    async def rollback() -> None:
        return None

    service = RequiredPasswordChangeService(
        user_repository=FakeUserRepository(
            user
        ),
        refresh_repository=FakeRefreshRepository(),
        commit=commit,
        rollback=rollback,
    )

    with pytest.raises(
        PasswordChangeRejectedError
    ):
        await service.replace_required_password(
            user_id=user.id,
            current_password="wrong",
            new_password="NeuroVest-Strong!2026",
        )

    assert user.must_change_password is True
