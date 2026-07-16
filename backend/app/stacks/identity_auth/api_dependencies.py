from __future__ import annotations

from collections.abc import (
    AsyncIterator,
)
from typing import Any

from fastapi import (
    Depends,
    HTTPException,
    status,
)

from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from backend.app.stacks.identity_auth.dependencies import (
    authenticate_bearer_credentials,
)

from backend.app.stacks.identity_auth.access_token_revocation_repository import (
    AccessTokenRevocationRepository,
)

from backend.app.stacks.identity_auth.login_service import (
    LoginService,
)

from backend.app.stacks.identity_auth.registration_service import (
    RegistrationService,
)

from backend.app.stacks.identity_auth.session_lifecycle_service import (
    SessionLifecycleService,
)

from backend.app.stacks.db_runtime.database import (
    async_session,
)

from backend.app.stacks.identity_auth.repositories import (
    IdentityUserRepository,
    RefreshSessionRepository,
)

from backend.app.stacks.identity_auth.password_change_service import (
    RequiredPasswordChangeService,
)

from backend.app.stacks.identity_auth.runtime_adapter import (
    authentication_runtime,
    session_lifecycle_runtime,
)


bearer_scheme = HTTPBearer(
    auto_error=False
)


async def get_registration_api_service() -> AsyncIterator[
    RegistrationService
]:
    """
    Bind one real registration service to one API request.

    The surrounding authentication runtime owns the
    database-session lifetime. The service owns commit and
    rollback behavior for its authorized operation.
    """

    async with authentication_runtime() as runtime:
        registration_service, _ = runtime

        yield registration_service


async def get_login_api_service() -> AsyncIterator[
    LoginService
]:
    """
    Bind one real login service to one API request.

    The surrounding authentication runtime owns the
    database-session lifetime. The service owns commit and
    rollback behavior for its authorized operation.
    """

    async with authentication_runtime() as runtime:
        _, login_service = runtime

        yield login_service


async def require_authenticated_principal(
    credentials: (
        HTTPAuthorizationCredentials
        | None
    ) = Depends(
        bearer_scheme
    ),
) -> Any:
    """
    Validate only a bearer access token through the
    canonical identity-auth dependency.

    Missing, malformed, expired, refresh, or otherwise
    invalid credentials fail closed as HTTP 401.
    """

    if credentials is None:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail="Authentication required",
            headers={
                "WWW-Authenticate": "Bearer",
            },
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
            async with async_session() as session:
                repository = (
                    AccessTokenRevocationRepository(
                        session
                    )
                )

                if await repository.is_revoked(
                    token_id
                ):
                    raise HTTPException(
                        status_code=(
                            status.HTTP_401_UNAUTHORIZED
                        ),
                        detail=(
                            "Invalid authentication credentials"
                        ),
                        headers={
                            "WWW-Authenticate": "Bearer",
                        },
                    )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail="Invalid authentication credentials",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from exc

    if principal is None:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail="Invalid authentication credentials",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    return principal


async def optional_logout_access_principal(
    credentials: (
        HTTPAuthorizationCredentials
        | None
    ) = Depends(
        bearer_scheme
    ),
) -> Any | None:
    """
    Validate an optional access token for logout metadata.

    This dependency intentionally does not reject an already revoked
    JTI, allowing repeated logout requests to remain idempotent.
    """

    if credentials is None:
        return None

    try:
        return authenticate_bearer_credentials(
            credentials
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail="Invalid authentication credentials",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from exc


async def get_session_lifecycle_api_service() -> AsyncIterator[
    SessionLifecycleService
]:
    async with session_lifecycle_runtime() as service:
        yield service

async def get_required_password_change_service() -> AsyncIterator[
    RequiredPasswordChangeService
]:
    async with async_session() as session:
        yield RequiredPasswordChangeService(
            user_repository=IdentityUserRepository(
                session
            ),
            refresh_repository=RefreshSessionRepository(
                session
            ),
            commit=session.commit,
            rollback=session.rollback,
        )

