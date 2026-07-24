from __future__ import annotations

from backend.app.stacks.identity_auth.authorization_policy import (
    ADMINISTRATIVE_ROLES,
    canonical_role_value,
    is_administrative_role,
)

from dataclasses import dataclass
from typing import AsyncIterator

from fastapi import (
    Depends,
    HTTPException,
    status,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.stacks.db_runtime.database import (
    async_session,
)
from backend.app.stacks.identity_auth.admin_read_models import (
    AdministrativeReadService,
)

from backend.app.stacks.identity_auth.access_token_revocation_repository import (
    AccessTokenRevocationRepository,
)
from backend.app.stacks.identity_auth.models import (
    IdentityUser,
)
from backend.app.stacks.identity_auth.route_protection import (
    authenticate_bearer_credentials,
)


_bearer = HTTPBearer(
    auto_error=False,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AdministrativePrincipal:
    user_id: str
    role: str


async def administrative_database_session() -> (
    AsyncIterator[AsyncSession]
):
    async with async_session() as session:
        yield session


async def require_administrative_principal(
    credentials: (
        HTTPAuthorizationCredentials
        | None
    ) = Depends(
        _bearer
    ),
    session: AsyncSession = Depends(
        administrative_database_session
    ),
) -> AdministrativePrincipal:
    if credentials is None:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail="Authentication required",
        )

    try:
        principal = (
            authenticate_bearer_credentials(
                credentials
            )
        )

        token_id = getattr(
            principal,
            "token_id",
            None,
        )

        if token_id:
            revocation_repository = (
                AccessTokenRevocationRepository(
                    session
                )
            )

            if await revocation_repository.is_revoked(
                token_id
            ):
                raise HTTPException(
                    status_code=(
                        status.HTTP_401_UNAUTHORIZED
                    ),
                    detail="Authentication failed",
                )
    except Exception as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail="Authentication failed",
        ) from exc

    subject = str(
        getattr(
            principal,
            "subject",
            "",
        )
    ).strip()

    if not subject:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail="Authentication failed",
        )

    result = await session.execute(
        select(
            IdentityUser
        ).where(
            IdentityUser.id == subject
        )
    )

    user = result.scalar_one_or_none()

    if (
        user is None
        or user.is_active is not True
        or user.status != "active"
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail="Authentication failed",
        )

    if bool(
        getattr(
            user,
            "must_change_password",
            False,
        )
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail="Password change required",
        )

    role = str(
        getattr(
            user,
            "role",
            "",
        )
    ).strip().lower()

    if not is_administrative_role(
        role
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail="Administrative access denied",
        )

    canonical_role = canonical_role_value(
        role
    )

    if canonical_role is None:
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail="Administrative access denied",
        )

    return AdministrativePrincipal(
        user_id=subject,
        role=canonical_role,
    )


def get_administrative_read_service(
    session: AsyncSession = Depends(
        administrative_database_session
    ),
) -> AdministrativeReadService:
    return AdministrativeReadService(
        session
    )
