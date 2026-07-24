from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import (
    delete,
    select,
)
from sqlalchemy import func
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from backend.app.stacks.identity_auth.access_token_revocation_models import (
    IdentityAccessTokenRevocation,
)


def _utc_now_naive() -> datetime:
    return datetime.now(
        UTC
    ).replace(
        tzinfo=None
    )


def _normalize_datetime(
    value: datetime,
) -> datetime:
    if value.tzinfo is None:
        return value

    return value.astimezone(
        UTC
    ).replace(
        tzinfo=None
    )


class AccessTokenRevocationRepository:
    """
    Durable repository for access-token JTI revocation records.

    Transaction ownership remains with the caller. Repository methods
    flush changes but do not commit the database session.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def revoke(
        self,
        *,
        token_id: str,
        user_id: str,
        issued_at: datetime,
        expires_at: datetime,
        revoked_at: datetime | None = None,
        reason: str = "logout",
    ) -> IdentityAccessTokenRevocation:
        normalized_token_id = (
            token_id.strip()
        )

        normalized_user_id = (
            user_id.strip()
        )

        normalized_reason = (
            reason.strip()
        )

        if not normalized_token_id:
            raise ValueError(
                "Token identifier cannot be empty"
            )

        if not normalized_user_id:
            raise ValueError(
                "User identifier cannot be empty"
            )

        if not normalized_reason:
            raise ValueError(
                "Revocation reason cannot be empty"
            )

        if len(normalized_reason) > 64:
            raise ValueError(
                "Revocation reason exceeds 64 characters"
            )

        normalized_issued_at = (
            _normalize_datetime(
                issued_at
            )
        )

        normalized_expires_at = (
            _normalize_datetime(
                expires_at
            )
        )

        normalized_revoked_at = (
            _normalize_datetime(
                revoked_at
            )
            if revoked_at is not None
            else _utc_now_naive()
        )

        if (
            normalized_expires_at
            <= normalized_issued_at
        ):
            raise ValueError(
                "Access-token expiry must occur after issuance"
            )

        existing = await self.get_by_token_id(
            normalized_token_id
        )

        if existing is not None:
            return existing

        record = IdentityAccessTokenRevocation(
            token_id=normalized_token_id,
            user_id=normalized_user_id,
            issued_at=normalized_issued_at,
            expires_at=normalized_expires_at,
            revoked_at=normalized_revoked_at,
            reason=normalized_reason,
        )

        self._session.add(
            record
        )

        await self._session.flush()

        return record

    async def get_by_token_id(
        self,
        token_id: str,
    ) -> IdentityAccessTokenRevocation | None:
        normalized_token_id = (
            token_id.strip()
        )

        if not normalized_token_id:
            return None

        result = await self._session.execute(
            select(
                IdentityAccessTokenRevocation
            ).where(
                IdentityAccessTokenRevocation.token_id
                == normalized_token_id
            )
        )

        return result.scalar_one_or_none()

    async def is_revoked(
        self,
        token_id: str,
        *,
        at: datetime | None = None,
    ) -> bool:
        record = await self.get_by_token_id(
            token_id
        )

        if record is None:
            return False

        comparison_time = (
            _normalize_datetime(
                at
            )
            if at is not None
            else _utc_now_naive()
        )

        return (
            record.revoked_at
            <= comparison_time
            < record.expires_at
        )

    async def cleanup_expired(
        self,
        *,
        at: datetime | None = None,
    ) -> int:
        comparison_time = (
            _normalize_datetime(
                at
            )
            if at is not None
            else _utc_now_naive()
        )

        result = await self._session.execute(
            delete(
                IdentityAccessTokenRevocation
            ).where(
                IdentityAccessTokenRevocation.expires_at
                <= comparison_time
            )
        )

        await self._session.flush()

        rowcount = getattr(
            result,
            "rowcount",
            0,
        )

        return int(
            rowcount or 0
        )

    # IQC STAGE 5B-C ADMINISTRATIVE REVOCATION READ METHODS
    async def list_records(
        self,
        *,
        offset: int,
        limit: int,
        user_id: str | None = None,
        state: str | None = None,
        at: datetime | None = None,
    ) -> tuple[
        list[IdentityAccessTokenRevocation],
        int,
    ]:
        if offset < 0:
            raise ValueError(
                "Offset cannot be negative"
            )

        if limit < 1 or limit > 100:
            raise ValueError(
                "Limit must be between 1 and 100"
            )

        comparison_time = (
            _normalize_datetime(
                at
            )
            if at is not None
            else _utc_now_naive()
        )

        filters = []

        if user_id is not None:
            normalized_user_id = (
                user_id.strip()
            )

            if not normalized_user_id:
                raise ValueError(
                    "User identifier cannot be empty"
                )

            filters.append(
                IdentityAccessTokenRevocation.user_id
                == normalized_user_id
            )

        if state is not None:
            normalized_state = (
                state.strip().lower()
            )

            if normalized_state == "active":
                filters.append(
                    IdentityAccessTokenRevocation.expires_at
                    > comparison_time
                )

            elif normalized_state == "expired":
                filters.append(
                    IdentityAccessTokenRevocation.expires_at
                    <= comparison_time
                )

            else:
                raise ValueError(
                    "Unsupported revocation state"
                )

        count_statement = (
            select(
                func.count()
            )
            .select_from(
                IdentityAccessTokenRevocation
            )
        )

        list_statement = (
            select(
                IdentityAccessTokenRevocation
            )
            .order_by(
                IdentityAccessTokenRevocation.revoked_at.desc(),
                IdentityAccessTokenRevocation.id.desc(),
            )
            .offset(
                offset
            )
            .limit(
                limit
            )
        )

        if filters:
            count_statement = (
                count_statement.where(
                    *filters
                )
            )

            list_statement = (
                list_statement.where(
                    *filters
                )
            )

        count_result = await self._session.execute(
            count_statement
        )

        total = int(
            count_result.scalar_one()
        )

        list_result = await self._session.execute(
            list_statement
        )

        records = list(
            list_result.scalars().all()
        )

        return records, total

    async def get_by_id(
        self,
        revocation_id: str,
    ) -> IdentityAccessTokenRevocation | None:
        normalized_id = (
            revocation_id.strip()
        )

        if not normalized_id:
            return None

        result = await self._session.execute(
            select(
                IdentityAccessTokenRevocation
            ).where(
                IdentityAccessTokenRevocation.id
                == normalized_id
            )
        )

        return result.scalar_one_or_none()
