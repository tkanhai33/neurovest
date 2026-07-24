from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from backend.app.stacks.identity_auth.models import (
    IdentityRefreshSession,
)

from backend.app.stacks.identity_auth.repositories import (
    RefreshSessionRepository,
)


class RefreshSessionError(Exception):
    """Base refresh-session persistence error."""


class RefreshSessionNotFoundError(
    RefreshSessionError
):
    """Raised when a refresh session does not exist."""


class RefreshSessionExpiredError(
    RefreshSessionError
):
    """Raised when a refresh session is expired."""


class RefreshTokenReuseDetectedError(
    RefreshSessionError
):
    """Raised when a revoked refresh token is reused."""


@dataclass(frozen=True)
class RotationResult:
    previous_token_id: str
    replacement_token_id: str
    family_id: str


class RefreshSessionService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

        self._repository = (
            RefreshSessionRepository(
                session
            )
        )

    async def rotate(
        self,
        *,
        current_token_id: str,
        replacement_token_id: str,
        replacement_token_hash: str,
        replacement_issued_at: datetime,
        replacement_expires_at: datetime,
    ) -> RotationResult:
        current = (
            await self._repository.get_by_token_id(
                current_token_id,
                for_update=True,
            )
        )

        if current is None:
            raise RefreshSessionNotFoundError(
                "Refresh session was not found"
            )

        now = datetime.now(
            UTC
        )

        if current.revoked_at is not None:
            await self._repository.revoke_family(
                current.family_id,
                revoked_at=now,
            )

            raise RefreshTokenReuseDetectedError(
                "Revoked refresh token was reused"
            )

        if current.expires_at <= now:
            await self._repository.revoke(
                current,
                revoked_at=now,
            )

            raise RefreshSessionExpiredError(
                "Refresh session has expired"
            )

        replacement = await self._repository.create(
            user_id=current.user_id,
            token_id=replacement_token_id,
            token_hash=replacement_token_hash,
            family_id=current.family_id,
            issued_at=replacement_issued_at,
            expires_at=replacement_expires_at,
        )

        await self._repository.revoke(
            current,
            revoked_at=now,
            replaced_by=replacement.token_id,
        )

        return RotationResult(
            previous_token_id=current.token_id,
            replacement_token_id=(
                replacement.token_id
            ),
            family_id=current.family_id,
        )

    async def logout(
        self,
        *,
        token_id: str,
    ) -> None:
        record = (
            await self._repository.get_by_token_id(
                token_id,
                for_update=True,
            )
        )

        if record is None:
            return

        if record.revoked_at is None:
            await self._repository.revoke(
                record,
                revoked_at=datetime.now(
                    UTC
                ),
            )

    async def revoke_all(
        self,
        *,
        user_id: str,
    ) -> int:
        return (
            await self._repository.revoke_all_for_user(
                user_id,
                revoked_at=datetime.now(
                    UTC
                ),
            )
        )


    async def cleanup_expired(
        self,
        *,
        before: datetime | None = None,
    ) -> int:
        return await self._repository.delete_expired(
            before=before
        )
