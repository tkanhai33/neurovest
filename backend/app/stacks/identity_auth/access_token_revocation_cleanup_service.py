from __future__ import annotations

from datetime import datetime

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from backend.app.stacks.identity_auth.access_token_revocation_repository import (
    AccessTokenRevocationRepository,
)


class AccessTokenRevocationCleanupService:
    """
    Transactional expired-revocation cleanup boundary.

    This service is not exposed as an administrative mutation route.
    The supplied request or maintenance session owns the transaction.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session
        self._repository = (
            AccessTokenRevocationRepository(
                session
            )
        )

    async def cleanup_expired(
        self,
        *,
        at: datetime | None = None,
    ) -> int:
        try:
            deleted = (
                await self._repository.cleanup_expired(
                    at=at
                )
            )

            await self._session.commit()

            return deleted

        except Exception:
            await self._session.rollback()
            raise
