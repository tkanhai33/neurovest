from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime

from backend.app.stacks.identity_auth.passwords import (
    hash_password,
    verify_password,
)

from backend.app.stacks.identity_auth.repositories import (
    IdentityUserRepository,
    RefreshSessionRepository,
)


class PasswordChangeRejectedError(Exception):
    """Fail-closed password replacement rejection."""


@dataclass(
    frozen=True,
    slots=True,
)
class PasswordChangeResult:
    user_id: str
    revoked_sessions: int
    changed_at: datetime


def validate_replacement_password(
    password: str,
) -> None:
    if not isinstance(
        password,
        str,
    ):
        raise PasswordChangeRejectedError(
            "Password replacement was rejected"
        )

    checks = (
        len(password) >= 12,
        len(password) <= 1024,
        bool(re.search(r"[A-Z]", password)),
        bool(re.search(r"[a-z]", password)),
        bool(re.search(r"[0-9]", password)),
        bool(re.search(r"[^A-Za-z0-9]", password)),
    )

    if not all(checks):
        raise PasswordChangeRejectedError(
            "Password replacement was rejected"
        )


class RequiredPasswordChangeService:
    def __init__(
        self,
        *,
        user_repository: IdentityUserRepository,
        refresh_repository: RefreshSessionRepository,
        commit,
        rollback,
    ) -> None:
        self._user_repository = user_repository
        self._refresh_repository = refresh_repository
        self._commit = commit
        self._rollback = rollback

    async def replace_required_password(
        self,
        *,
        user_id: str,
        current_password: str,
        new_password: str,
    ) -> PasswordChangeResult:
        try:
            validate_replacement_password(
                new_password
            )

            if (
                not isinstance(
                    current_password,
                    str,
                )
                or not current_password
                or current_password
                == new_password
            ):
                raise PasswordChangeRejectedError(
                    "Password replacement was rejected"
                )

            user = await self._user_repository.get_by_id(
                user_id
            )

            if (
                user is None
                or user.is_active is not True
                or user.status != "active"
                or user.must_change_password is not True
            ):
                raise PasswordChangeRejectedError(
                    "Password replacement was rejected"
                )

            if not verify_password(
                current_password,
                user.password_hash,
            ):
                raise PasswordChangeRejectedError(
                    "Password replacement was rejected"
                )

            if verify_password(
                new_password,
                user.password_hash,
            ):
                raise PasswordChangeRejectedError(
                    "Password replacement was rejected"
                )

            replacement_hash = hash_password(
                new_password
            )

            await self._user_repository.update_password_hash(
                user,
                password_hash=replacement_hash,
            )

            await self._user_repository.update_identity_security_state(
                user,
                must_change_password=False,
            )

            changed_at = datetime.now(
                UTC
            )

            revoked = (
                await self._refresh_repository.revoke_all_for_user(
                    user.id,
                    revoked_at=changed_at,
                )
            )

            await self._commit()

            return PasswordChangeResult(
                user_id=user.id,
                revoked_sessions=revoked,
                changed_at=changed_at,
            )

        except PasswordChangeRejectedError:
            await self._rollback()
            raise

        except Exception as exc:
            await self._rollback()

            raise PasswordChangeRejectedError(
                "Password replacement was rejected"
            ) from exc
