from __future__ import annotations

from fastapi import HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from backend.app.stacks.identity_auth.contracts import (
    AuthenticatedPrincipal,
)

from backend.app.stacks.identity_auth.errors import (
    AuthenticationError,
)

from backend.app.stacks.identity_auth.revocation import (
    InMemoryTokenRevocationStore,
)

from backend.app.stacks.identity_auth.tokens import (
    validate_access_token,
)


bearer_scheme = HTTPBearer(
    auto_error=False
)


def authenticate_bearer_credentials(
    credentials: (
        HTTPAuthorizationCredentials
        | None
    ),
    *,
    revocation_store: (
        InMemoryTokenRevocationStore
        | None
    ) = None,
) -> AuthenticatedPrincipal:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unsupported authentication scheme",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    try:
        claims = validate_access_token(
            credentials.credentials,
            revocation_store=revocation_store,
        )

    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from exc

    return AuthenticatedPrincipal(
        subject=claims.subject,
        token_id=claims.token_id,
        claims=claims.extra,
        issued_at=claims.issued_at,
        expires_at=claims.expires_at,
    )


def require_authenticated_principal(
    credentials: (
        HTTPAuthorizationCredentials
        | None
    ),
) -> AuthenticatedPrincipal:
    return authenticate_bearer_credentials(
        credentials
    )
