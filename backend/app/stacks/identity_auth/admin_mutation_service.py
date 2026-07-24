from __future__ import annotations

import logging
import secrets
import string
from datetime import UTC, datetime
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.stacks.identity_auth.access_token_revocation_models import (
    IdentityAccessTokenRevocation,
)
from backend.app.stacks.identity_auth.admin_mutation_api_models import (
    AdministrativeDeleteResponse,
    AdministrativeMutationResponse,
    AdministrativeTemporaryPasswordResponse,
)
from backend.app.stacks.identity_auth.models import (
    IdentityRefreshSession,
    IdentityUser,
)
from backend.app.stacks.identity_auth.passwords import (
    hash_password,
)


logger = logging.getLogger(
    "neurovest.identity.admin_mutation"
)

PROTECTED_ROLES = {
    "dev",
    "developer",
    "owner",
}

ADMINISTRATIVE_ROLES = {
    "admin",
    "administrator",
    "owner",
    "dev",
    "developer",
}


def _normalized_role(value: Any) -> str:
    enum_value = getattr(
        value,
        "value",
        value,
    )

    return str(
        enum_value or ""
    ).strip().lower()


def _principal_subject(
    principal: Any,
) -> str:
    subject = (
        getattr(principal, "subject", None)
        or getattr(principal, "user_id", None)
        or getattr(principal, "id", None)
    )

    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Administrative principal "
                "identity is unavailable"
            ),
        )

    return str(subject)


def _principal_role(
    principal: Any,
) -> str:
    role = _normalized_role(
        getattr(principal, "role", None)
    )

    if role:
        return role

    claims = getattr(
        principal,
        "claims",
        {},
    )

    if isinstance(claims, dict):
        return _normalized_role(
            claims.get("role")
        )

    return ""


def _generate_temporary_password() -> str:
    alphabet = (
        string.ascii_letters
        + string.digits
        + "!@#$%^&*"
    )

    while True:
        password = "".join(
            secrets.choice(alphabet)
            for _ in range(24)
        )

        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and any(c.isdigit() for c in password)
            and any(c in "!@#$%^&*" for c in password)
        ):
            return password


def _set_status(
    user: IdentityUser,
    value: str,
) -> None:
    current = getattr(
        user,
        "status",
        None,
    )

    enum_type = type(current)

    if hasattr(enum_type, "__members__"):
        members = enum_type.__members__

        for candidate in (
            value.upper(),
            value.lower(),
        ):
            if candidate in members:
                user.status = members[candidate]
                return

    user.status = value


class AdministrativeUserMutationService:
    def __init__(
        self,
        *,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def _load_target(
        self,
        *,
        user_id: str,
    ) -> IdentityUser:
        result = await self._session.execute(
            select(
                IdentityUser
            ).where(
                IdentityUser.id == user_id
            )
        )

        target = result.scalar_one_or_none()

        if target is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return target

    def _authorize_actor(
        self,
        principal: Any,
    ) -> tuple[str, str]:
        actor_id = _principal_subject(
            principal
        )

        actor_role = _principal_role(
            principal
        )

        if actor_role not in ADMINISTRATIVE_ROLES:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Administrative access "
                    "is required"
                ),
            )

        return actor_id, actor_role

    def _assert_target_mutable(
        self,
        *,
        actor_id: str,
        target: IdentityUser,
    ) -> None:
        target_role = _normalized_role(
            getattr(target, "role", None)
        )

        if target_role in PROTECTED_ROLES:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Protected Dev or Owner "
                    "accounts cannot be mutated"
                ),
            )

        if str(target.id) == actor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Administrative self-mutation "
                    "is not permitted"
                ),
            )

    async def _revoke_refresh_sessions(
        self,
        *,
        user_id: str,
    ) -> int:
        now = datetime.now(UTC)

        result = await self._session.execute(
            update(
                IdentityRefreshSession
            )
            .where(
                IdentityRefreshSession.user_id
                == user_id
            )
            .where(
                IdentityRefreshSession.revoked_at
                .is_(None)
            )
            .values(
                revoked_at=now,
                last_used_at=now,
            )
        )

        return int(
            result.rowcount or 0
        )

    def _audit(
        self,
        *,
        action: str,
        actor_id: str,
        target_id: str,
    ) -> None:
        logger.info(
            "administrative_identity_mutation",
            extra={
                "action": action,
                "actor_user_id": actor_id,
                "target_user_id": target_id,
                "secret_material_included": False,
            },
        )

    async def require_password_reset(
        self,
        *,
        principal: Any,
        user_id: str,
    ) -> AdministrativeMutationResponse:
        actor_id, _ = self._authorize_actor(
            principal
        )

        target = await self._load_target(
            user_id=user_id
        )

        self._assert_target_mutable(
            actor_id=actor_id,
            target=target,
        )

        try:
            target.must_change_password = True

            revoked = (
                await self._revoke_refresh_sessions(
                    user_id=user_id
                )
            )

            await self._session.commit()

            self._audit(
                action="require_password_reset",
                actor_id=actor_id,
                target_id=user_id,
            )

            return AdministrativeMutationResponse(
                status="completed",
                action="require_password_reset",
                user_id=user_id,
                sessions_revoked=revoked,
            )
        except HTTPException:
            raise
        except Exception:
            await self._session.rollback()
            raise

    async def issue_temporary_password(
        self,
        *,
        principal: Any,
        user_id: str,
    ) -> AdministrativeTemporaryPasswordResponse:
        actor_id, _ = self._authorize_actor(
            principal
        )

        target = await self._load_target(
            user_id=user_id
        )

        self._assert_target_mutable(
            actor_id=actor_id,
            target=target,
        )

        temporary_password = (
            _generate_temporary_password()
        )

        try:
            target.password_hash = hash_password(
                temporary_password
            )
            target.must_change_password = True

            revoked = (
                await self._revoke_refresh_sessions(
                    user_id=user_id
                )
            )

            await self._session.commit()

            self._audit(
                action="issue_temporary_password",
                actor_id=actor_id,
                target_id=user_id,
            )

            return AdministrativeTemporaryPasswordResponse(
                status="completed",
                action="issue_temporary_password",
                user_id=user_id,
                sessions_revoked=revoked,
                temporary_password=temporary_password,
                must_change_password=True,
            )
        except HTTPException:
            raise
        except Exception:
            await self._session.rollback()
            raise

    async def disable_account(
        self,
        *,
        principal: Any,
        user_id: str,
    ) -> AdministrativeMutationResponse:
        actor_id, _ = self._authorize_actor(
            principal
        )

        target = await self._load_target(
            user_id=user_id
        )

        self._assert_target_mutable(
            actor_id=actor_id,
            target=target,
        )

        try:
            target.is_active = False
            _set_status(target, "disabled")

            revoked = (
                await self._revoke_refresh_sessions(
                    user_id=user_id
                )
            )

            await self._session.commit()

            self._audit(
                action="disable_account",
                actor_id=actor_id,
                target_id=user_id,
            )

            return AdministrativeMutationResponse(
                status="completed",
                action="disable_account",
                user_id=user_id,
                sessions_revoked=revoked,
            )
        except HTTPException:
            raise
        except Exception:
            await self._session.rollback()
            raise

    async def enable_account(
        self,
        *,
        principal: Any,
        user_id: str,
    ) -> AdministrativeMutationResponse:
        actor_id, _ = self._authorize_actor(
            principal
        )

        target = await self._load_target(
            user_id=user_id
        )

        self._assert_target_mutable(
            actor_id=actor_id,
            target=target,
        )

        try:
            target.is_active = True
            _set_status(target, "active")

            await self._session.commit()

            self._audit(
                action="enable_account",
                actor_id=actor_id,
                target_id=user_id,
            )

            return AdministrativeMutationResponse(
                status="completed",
                action="enable_account",
                user_id=user_id,
                sessions_revoked=0,
            )
        except HTTPException:
            raise
        except Exception:
            await self._session.rollback()
            raise

    async def delete_account(
        self,
        *,
        principal: Any,
        user_id: str,
    ) -> AdministrativeDeleteResponse:
        actor_id, _ = self._authorize_actor(
            principal
        )

        target = await self._load_target(
            user_id=user_id
        )

        self._assert_target_mutable(
            actor_id=actor_id,
            target=target,
        )

        try:
            await self._session.execute(
                delete(
                    IdentityAccessTokenRevocation
                ).where(
                    IdentityAccessTokenRevocation.user_id
                    == user_id
                )
            )

            await self._session.execute(
                delete(
                    IdentityRefreshSession
                ).where(
                    IdentityRefreshSession.user_id
                    == user_id
                )
            )

            await self._session.delete(target)
            await self._session.commit()

            self._audit(
                action="delete_account",
                actor_id=actor_id,
                target_id=user_id,
            )

            return AdministrativeDeleteResponse(
                status="completed",
                action="delete_account",
                user_id=user_id,
                deleted=True,
            )
        except HTTPException:
            raise
        except Exception:
            await self._session.rollback()
            raise
