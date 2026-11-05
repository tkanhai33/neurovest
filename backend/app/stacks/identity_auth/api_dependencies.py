from __future__ import annotations

from collections.abc import (
    AsyncIterator,
)
from typing import Any

import os
from fastapi import Request

from backend.app.stacks.chat_public import public_controls as public_controls_module
from backend.app.stacks.chat_public.public_controls import (
    AnonymousSlidingWindowLimiter,
    PublicChatRateLimited,
)


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




_AUTH_LIMITER = AnonymousSlidingWindowLimiter(
    limit=int(
        os.getenv(
            "NEUROVEST_AUTH_RATE_LIMIT",
            "10",
        )
    ),
    window_seconds=float(
        os.getenv(
            "NEUROVEST_AUTH_RATE_WINDOW_SECONDS",
            "60",
        )
    ),
)


async def enforce_auth_rate_limit(
    request: Request,
) -> None:
    """
    Apply the authentication request limit by normalized client IP.

    The exception type is resolved through the public-controls module
    at runtime so test or development module reloads cannot produce a
    stale exception-class reference.
    """

    client = "anonymous"

    if (
        request.client is not None
        and request.client.host
    ):
        client = (
            str(
                request.client.host
            ).strip()
            or "anonymous"
        )

    # Separate public proxy traffic from direct clients.
    # Untrusted forwarding headers are deliberately ignored.
    # Aggregate public traffic gets a larger bounded allowance;
    # direct clients retain the existing per-client limit.
    if client in {"127.0.0.1", "::1"}:
        aggregate_limit = int(
            os.getenv("NEUROVEST_PUBLIC_AUTH_AGGREGATE_LIMIT", "300")
        )
        if aggregate_limit < 10 or aggregate_limit > 10000:
            raise HTTPException(
                status_code=503,
                detail="Invalid authentication protection configuration",
            )

        from backend.app.stacks.chat_public.public_controls import (
            AnonymousSlidingWindowLimiter,
        )

        aggregate = globals().get("_PUBLIC_AUTH_AGGREGATE_LIMITER")
        if aggregate is None:
            aggregate = AnonymousSlidingWindowLimiter(
                limit=aggregate_limit,
                window_seconds=60,
            )
            globals()["_PUBLIC_AUTH_AGGREGATE_LIMITER"] = aggregate

        limiter = aggregate
        limiter_client = "public_proxy_aggregate"
    else:
        limiter = _AUTH_LIMITER
        limiter_client = client

    try:
        limiter.check(
            limiter_client
        )

    except (
        public_controls_module
        .PublicChatRateLimited
    ) as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_429_TOO_MANY_REQUESTS
            ),
            detail=(
                "Too many authentication requests"
            ),
            headers={
                "Retry-After": "60",
            },
        ) from exc



def reset_auth_rate_limiter() -> None:
    """Clear process-local authentication limiter state for tests."""

    _AUTH_LIMITER.reset()



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


from backend.app.stacks.identity_auth.credential_generation import assert_token_generation

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

    # F12-R3H: account-wide access-token invalidation
    _f12_verified_principal = principal

    _f12_owner = getattr(
        _f12_verified_principal, "subject", None
    )

    _f12_issued_at = getattr(
        _f12_verified_principal, "issued_at", None
    )

    if not isinstance(_f12_owner, str) or not _f12_owner:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
        )

    async with async_session() as _f12_db:
        await assert_token_generation(
            _f12_db,
            user_id=_f12_owner,
            claims=_f12_verified_principal.claims,
        )

    return _f12_verified_principal


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

# New dependency for session repository
async def get_session_repository() -> AsyncIterator[IdentityUserRepository]:
    async with async_session() as session:
        yield IdentityUserRepository(session)
