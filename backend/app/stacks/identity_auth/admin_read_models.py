from __future__ import annotations

from datetime import UTC, datetime

from datetime import (
    UTC,
    datetime,
)
from typing import Any

from sqlalchemy import (
    func,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.stacks.identity_auth.admin_read_api_models import (
    AdministrativeSessionDetail,
    AdministrativeSessionListResponse,
    AdministrativeSessionSummary,
    AdministrativeUserDetail,
    AdministrativeUserListResponse,
    AdministrativeUserSummary,
)
from backend.app.stacks.identity_auth.admin_read_api_models import (
    AdministrativeAccessTokenRevocationDetail,
    AdministrativeAccessTokenRevocationListResponse,
    AdministrativeAccessTokenRevocationSummary,
)
from backend.app.stacks.identity_auth.access_token_revocation_repository import (
    AccessTokenRevocationRepository,
)

from backend.app.stacks.identity_auth.models import (
    IdentityRefreshSession,
    IdentityUser,
)


def _string_value(
    value: object,
    *,
    fallback: str = "",
) -> str:
    if value is None:
        return fallback

    rendered = str(value).strip()

    return rendered or fallback


def _datetime_value(
    value: object,
) -> datetime | None:
    if isinstance(
        value,
        datetime,
    ):
        return value

    return None


def _session_identifier(
    session: IdentityRefreshSession,
) -> str:
    for attribute in (
        "id",
        "token_id",
        "session_id",
    ):
        value = getattr(
            session,
            attribute,
            None,
        )

        if value is not None:
            return _string_value(
                value
            )

    raise RuntimeError(
        "Canonical session identifier is unavailable"
    )


def _session_family_identifier(
    session: IdentityRefreshSession,
) -> str | None:
    for attribute in (
        "family_id",
        "token_family_id",
    ):
        value = getattr(
            session,
            attribute,
            None,
        )

        if value is not None:
            return _string_value(
                value
            )

    return None


def _replacement_identifier(
    session: IdentityRefreshSession,
) -> str | None:
    for attribute in (
        "replaced_by_token_id",
        "replacement_token_id",
        "replaced_by_session_id",
    ):
        value = getattr(
            session,
            attribute,
            None,
        )

        if value is not None:
            return _string_value(
                value
            )

    return None


def _session_state(
    session: IdentityRefreshSession,
) -> str:
    revoked_at = _datetime_value(
        getattr(
            session,
            "revoked_at",
            None,
        )
    )

    if revoked_at is not None:
        return "revoked"

    expires_at = _datetime_value(
        getattr(
            session,
            "expires_at",
            None,
        )
    )

    if (
        expires_at is not None
        and expires_at <= datetime.now(
            UTC
        )
    ):
        return "expired"

    if (
        _replacement_identifier(
            session
        )
        is not None
    ):
        return "replaced"

    return "active"


def _user_summary(
    user: IdentityUser,
) -> AdministrativeUserSummary:
    return AdministrativeUserSummary(
        user_id=_string_value(
            user.id
        ),
        email=_string_value(
            user.email_normalized
        ),
        role=_string_value(
            getattr(
                user,
                "role",
                "user",
            ),
            fallback="user",
        ),
        status=_string_value(
            getattr(
                user,
                "status",
                "unknown",
            ),
            fallback="unknown",
        ),
        is_active=bool(
            getattr(
                user,
                "is_active",
                False,
            )
        ),
        must_change_password=bool(
            getattr(
                user,
                "must_change_password",
                False,
            )
        ),
        created_at=_datetime_value(
            getattr(
                user,
                "created_at",
                None,
            )
        ),
        updated_at=_datetime_value(
            getattr(
                user,
                "updated_at",
                None,
            )
        ),
    )


def _session_summary(
    session: IdentityRefreshSession,
) -> AdministrativeSessionSummary:
    replacement_id = (
        _replacement_identifier(
            session
        )
    )

    return AdministrativeSessionSummary(
        session_id=_session_identifier(
            session
        ),
        user_id=_string_value(
            session.user_id
        ),
        state=_session_state(
            session
        ),
        issued_at=_datetime_value(
            getattr(
                session,
                "issued_at",
                None,
            )
        ),
        expires_at=_datetime_value(
            getattr(
                session,
                "expires_at",
                None,
            )
        ),
        revoked_at=_datetime_value(
            getattr(
                session,
                "revoked_at",
                None,
            )
        ),
        replaced=(
            replacement_id
            is not None
        ),
    )


class AdministrativeReadService:
    __slots__ = (
        "_session",
    )

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def list_users(
        self,
        *,
        offset: int,
        limit: int,
    ) -> AdministrativeUserListResponse:
        total_statement = select(
            func.count()
        ).select_from(
            IdentityUser
        )

        total_result = await self._session.execute(
            total_statement
        )

        total = int(
            total_result.scalar_one()
        )

        statement = (
            select(
                IdentityUser
            )
            .order_by(
                IdentityUser.email_normalized.asc()
            )
            .offset(
                offset
            )
            .limit(
                limit
            )
        )

        result = await self._session.execute(
            statement
        )

        users = tuple(
            result.scalars().all()
        )

        items = tuple(
            _user_summary(
                user
            )
            for user in users
        )

        return AdministrativeUserListResponse(
            items=items,
            offset=offset,
            limit=limit,
            returned=len(items),
            total=total,
        )

    async def get_user(
        self,
        *,
        user_id: str,
    ) -> AdministrativeUserDetail | None:
        result = await self._session.execute(
            select(
                IdentityUser
            ).where(
                IdentityUser.id == user_id
            )
        )

        user = result.scalar_one_or_none()

        if user is None:
            return None

        total_result = await self._session.execute(
            select(
                func.count()
            )
            .select_from(
                IdentityRefreshSession
            )
            .where(
                IdentityRefreshSession.user_id
                == user_id
            )
        )

        total_session_count = int(
            total_result.scalar_one()
        )

        now = datetime.now(
            UTC
        )

        active_conditions: list[Any] = [
            IdentityRefreshSession.user_id
            == user_id,
            IdentityRefreshSession.revoked_at.is_(
                None
            ),
            IdentityRefreshSession.expires_at
            > now,
        ]

        active_result = await self._session.execute(
            select(
                func.count()
            )
            .select_from(
                IdentityRefreshSession
            )
            .where(
                *active_conditions
            )
        )

        active_session_count = int(
            active_result.scalar_one()
        )

        summary = _user_summary(
            user
        )

        return AdministrativeUserDetail(
            **summary.model_dump(),
            active_session_count=(
                active_session_count
            ),
            total_session_count=(
                total_session_count
            ),
        )

    async def list_sessions(
        self,
        *,
        offset: int,
        limit: int,
        user_id: str | None,
        state: str | None,
    ) -> AdministrativeSessionListResponse:
        statement = select(
            IdentityRefreshSession
        )

        if user_id is not None:
            statement = statement.where(
                IdentityRefreshSession.user_id
                == user_id
            )

        statement = (
            statement
            .order_by(
                IdentityRefreshSession.issued_at.desc()
            )
            .offset(
                offset
            )
            .limit(
                limit
            )
        )

        result = await self._session.execute(
            statement
        )

        sessions = tuple(
            result.scalars().all()
        )

        items = tuple(
            _session_summary(
                session
            )
            for session in sessions
        )

        if state is not None:
            items = tuple(
                item
                for item in items
                if item.state == state
            )

        return AdministrativeSessionListResponse(
            items=items,
            offset=offset,
            limit=limit,
            returned=len(items),
        )

    async def get_session(
        self,
        *,
        session_id: str,
    ) -> AdministrativeSessionDetail | None:
        identifier_column = getattr(
            IdentityRefreshSession,
            "id",
            None,
        )

        if identifier_column is None:
            identifier_column = getattr(
                IdentityRefreshSession,
                "token_id",
            )

        result = await self._session.execute(
            select(
                IdentityRefreshSession
            ).where(
                identifier_column == session_id
            )
        )

        session = result.scalar_one_or_none()

        if session is None:
            return None

        summary = _session_summary(
            session
        )

        return AdministrativeSessionDetail(
            **summary.model_dump(),
            token_family_id=(
                _session_family_identifier(
                    session
                )
            ),
            replacement_session_id=(
                _replacement_identifier(
                    session
                )
            ),
        )

    # IQC STAGE 5B-C ADMINISTRATIVE REVOCATION OBSERVABILITY
    @staticmethod
    def _revocation_state(
        expires_at: datetime,
        *,
        at: datetime | None = None,
    ) -> str:
        comparison_time = (
            at
            if at is not None
            else datetime.now(
                UTC
            ).replace(
                tzinfo=None
            )
        )

        normalized_expiry = (
            expires_at.replace(
                tzinfo=None
            )
            if expires_at.tzinfo is not None
            else expires_at
        )

        normalized_comparison = (
            comparison_time.replace(
                tzinfo=None
            )
            if comparison_time.tzinfo is not None
            else comparison_time
        )

        return (
            "expired"
            if normalized_expiry
            <= normalized_comparison
            else "active"
        )

    @classmethod
    def _revocation_summary(
        cls,
        record: object,
    ) -> AdministrativeAccessTokenRevocationSummary:
        return AdministrativeAccessTokenRevocationSummary(
            id=record.id,
            user_id=record.user_id,
            issued_at=record.issued_at,
            expires_at=record.expires_at,
            revoked_at=record.revoked_at,
            reason=record.reason,
            created_at=record.created_at,
            state=cls._revocation_state(
                record.expires_at
            ),
        )

    async def list_access_token_revocations(
        self,
        *,
        offset: int,
        limit: int,
        user_id: str | None = None,
        state: str | None = None,
    ) -> AdministrativeAccessTokenRevocationListResponse:
        repository = AccessTokenRevocationRepository(
            self._session
        )

        records, total = await repository.list_records(
            offset=offset,
            limit=limit,
            user_id=user_id,
            state=state,
        )

        return (
            AdministrativeAccessTokenRevocationListResponse(
                offset=offset,
                limit=limit,
                total=total,
                records=[
                    self._revocation_summary(
                        record
                    )
                    for record in records
                ],
            )
        )

    async def get_access_token_revocation(
        self,
        *,
        revocation_id: str,
    ) -> AdministrativeAccessTokenRevocationDetail | None:
        repository = AccessTokenRevocationRepository(
            self._session
        )

        record = await repository.get_by_id(
            revocation_id
        )

        if record is None:
            return None

        summary = self._revocation_summary(
            record
        )

        return AdministrativeAccessTokenRevocationDetail(
            **summary.model_dump()
        )
