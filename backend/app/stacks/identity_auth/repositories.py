from __future__ import annotations

# Restored canonical refresh-session repository dependencies.
from datetime import UTC as _refresh_UTC
from datetime import datetime as _refresh_datetime
from uuid import uuid4 as _refresh_uuid4

from sqlalchemy import (
    Select as _RefreshSelect,
    delete as _refresh_delete,
    select as _refresh_select,
    update as _refresh_update,
)

from backend.app.stacks.identity_auth.models import (
    IdentityRefreshSession as _IdentityRefreshSession,
)

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import (
    Select,
    select,
    update,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from backend.app.stacks.identity_auth.models import (
    IdentityRefreshSession,
    IdentityUser,
)

from backend.app.stacks.identity_auth.normalization import (
    normalize_email,
)


APPROVED_IDENTITY_ROLES = frozenset(
    {
        "user",
        "admin",
        "owner",
    }
)


def normalize_identity_role(
    role: str,
) -> str:
    if not isinstance(
        role,
        str,
    ):
        raise TypeError(
            "Identity role must be a string"
        )

    normalized = role.strip().lower()

    if normalized not in APPROVED_IDENTITY_ROLES:
        raise ValueError(
            "Unsupported identity role"
        )

    return normalized


class IdentityUserRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def create(
        self,
        *,
        email: str,
        password_hash: str,
        role: str = "user",
        must_change_password: bool = False,
        display_name: str | None = None,
    ) -> IdentityUser:
        if not password_hash:
            raise ValueError(
                "Password hash cannot be empty"
            )

        normalized_role = normalize_identity_role(
            role
        )

        user = IdentityUser(
            email_normalized=normalize_email(
                email
            ),
            password_hash=password_hash,
            status="active",
            is_active=True,
            role=normalized_role,
            must_change_password=bool(
                must_change_password
            ),
            display_name=display_name,
        )

        self._session.add(
            user
        )

        await self._session.flush()

        return user

    async def get_by_id(
        self,
        user_id: str,
    ) -> IdentityUser | None:
        return await self._session.get(
            IdentityUser,
            user_id,
        )

    async def get_by_email(
        self,
        email: str,
    ) -> IdentityUser | None:
        statement = select(
            IdentityUser
        ).where(
            IdentityUser.email_normalized
            == normalize_email(
                email
            )
        )

        return (
            await self._session.execute(
                statement
            )
        ).scalar_one_or_none()

    async def update_identity_security_state(
        self,
        user: IdentityUser,
        *,
        role: str | None = None,
        must_change_password: bool | None = None,
    ) -> IdentityUser:
        if role is not None:
            user.role = normalize_identity_role(
                role
            )

        if must_change_password is not None:
            user.must_change_password = bool(
                must_change_password
            )

        await self._session.flush()

        return user

    async def update_password_hash(
        self,
        user: IdentityUser,
        *,
        password_hash: str,
    ) -> IdentityUser:
        if not isinstance(
            password_hash,
            str,
        ) or not password_hash:
            raise ValueError(
                "Password hash cannot be empty"
            )

        user.password_hash = password_hash

        await self._session.flush()

        return user

class RefreshSessionRepository:
    """
    Canonical persistence boundary for durable refresh sessions.

    This restores the previously qualified public repository
    contract without changing the current IdentityUserRepository.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def create(
        self,
        *,
        user_id: str,
        token_id: str,
        token_hash: str,
        issued_at: _refresh_datetime,
        expires_at: _refresh_datetime,
        family_id: str | None = None,
    ) -> _IdentityRefreshSession:
        if not token_id:
            raise ValueError(
                "Token identifier cannot be empty"
            )

        if not token_hash:
            raise ValueError(
                "Token hash cannot be empty"
            )

        if expires_at <= issued_at:
            raise ValueError(
                "Refresh-session expiry must follow issuance"
            )

        record = _IdentityRefreshSession(
            user_id=user_id,
            token_id=token_id,
            token_hash=token_hash,
            family_id=(
                family_id
                or str(
                    _refresh_uuid4()
                )
            ),
            issued_at=issued_at,
            expires_at=expires_at,
        )

        self._session.add(
            record
        )

        await self._session.flush()

        return record

    async def get_by_token_id(
        self,
        token_id: str,
        *,
        for_update: bool = False,
    ) -> _IdentityRefreshSession | None:
        statement: _RefreshSelect = (
            _refresh_select(
                _IdentityRefreshSession
            )
            .where(
                _IdentityRefreshSession.token_id
                == token_id
            )
        )

        if for_update:
            statement = (
                statement.with_for_update()
            )

        return (
            await self._session.execute(
                statement
            )
        ).scalar_one_or_none()

    async def revoke(
        self,
        record: _IdentityRefreshSession,
        *,
        revoked_at: _refresh_datetime,
        replaced_by: str | None = None,
    ) -> None:
        record.revoked_at = revoked_at
        record.replaced_by = replaced_by
        record.last_used_at = revoked_at

        await self._session.flush()

    async def revoke_family(
        self,
        family_id: str,
        *,
        revoked_at: _refresh_datetime,
    ) -> int:
        result = await self._session.execute(
            _refresh_update(
                _IdentityRefreshSession
            )
            .where(
                _IdentityRefreshSession.family_id
                == family_id
            )
            .where(
                _IdentityRefreshSession.revoked_at
                .is_(
                    None
                )
            )
            .values(
                revoked_at=revoked_at,
                last_used_at=revoked_at,
            )
        )

        return int(
            result.rowcount
            or 0
        )

    async def revoke_all_for_user(
        self,
        user_id: str,
        *,
        revoked_at: _refresh_datetime,
    ) -> int:
        result = await self._session.execute(
            _refresh_update(
                _IdentityRefreshSession
            )
            .where(
                _IdentityRefreshSession.user_id
                == user_id
            )
            .where(
                _IdentityRefreshSession.revoked_at
                .is_(
                    None
                )
            )
            .values(
                revoked_at=revoked_at,
                last_used_at=revoked_at,
            )
        )

        return int(
            result.rowcount
            or 0
        )

    async def delete_expired(
        self,
        *,
        before: _refresh_datetime | None = None,
    ) -> int:
        threshold = (
            before
            or _refresh_datetime.now(
                _refresh_UTC
            )
        )

        result = await self._session.execute(
            _refresh_delete(
                _IdentityRefreshSession
            ).where(
                _IdentityRefreshSession.expires_at
                < threshold
            )
        )

        return int(
            result.rowcount
            or 0
        )
