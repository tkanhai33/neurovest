from __future__ import annotations

from collections.abc import (
    AsyncIterator,
    Mapping,
)
from contextlib import asynccontextmanager
from datetime import (
    UTC,
    datetime,
)
from typing import Any, Mapping

from backend.app.stacks.db_runtime.database import (
    async_session,
)

from backend.app.stacks.identity_auth.passwords import (
    hash_password,
    verify_password,
)

from backend.app.stacks.identity_auth.refresh_token_hashing import (
    hash_refresh_token,
)

from backend.app.stacks.identity_auth.secret_boundary import (
    load_jwt_secret,
)

from backend.app.stacks.identity_auth.tokens import (
    issue_access_token,
    issue_refresh_token,
    validate_access_token,
    validate_refresh_token,
)

from backend.app.stacks.identity_auth.repositories import (
    IdentityUserRepository,
    RefreshSessionRepository,
)

from backend.app.stacks.identity_auth.registration_service import (
    RegistrationService,
)

from backend.app.stacks.identity_auth.login_service import (
    LoginService,
)

from backend.app.stacks.identity_auth.service_contracts import (
    IssuedServiceToken,
)

from backend.app.stacks.identity_auth.refresh_token_hashing import (
    verify_refresh_token_hash,
)

from backend.app.stacks.identity_auth.session_service import (
    RefreshSessionService,
)

from backend.app.stacks.identity_auth.access_token_revocation_repository import (
    AccessTokenRevocationRepository,
)

from backend.app.stacks.identity_auth.session_lifecycle_service import (
    SessionLifecycleService,
    ValidatedRefreshIdentity,
)


def _claim_value(
    validated: Any,
    *names: str,
) -> Any:
    if isinstance(
        validated,
        Mapping,
    ):
        for name in names:
            if name in validated:
                return validated[
                    name
                ]

    nested = getattr(
        validated,
        "claims",
        None,
    )

    if isinstance(
        nested,
        Mapping,
    ):
        for name in names:
            if name in nested:
                return nested[
                    name
                ]

    payload = getattr(
        validated,
        "payload",
        None,
    )

    if isinstance(
        payload,
        Mapping,
    ):
        for name in names:
            if name in payload:
                return payload[
                    name
                ]

    for name in names:
        if hasattr(
            validated,
            name,
        ):
            return getattr(
                validated,
                name,
            )

    raise RuntimeError(
        "Required validated JWT claim is unavailable: "
        + ", ".join(
            names
        )
    )


def _as_identifier(
    value: Any,
) -> str:
    rendered = str(
        value
    ).strip()

    if not rendered:
        raise RuntimeError(
            "JWT token identifier is unavailable"
        )

    return rendered


def _as_datetime(
    value: Any,
) -> datetime:
    if isinstance(
        value,
        datetime,
    ):
        if value.tzinfo is None:
            return value.replace(
                tzinfo=UTC
            )

        return value

    if isinstance(
        value,
        (
            int,
            float,
        ),
    ):
        return datetime.fromtimestamp(
            value,
            tz=UTC,
        )

    raise RuntimeError(
        "JWT timestamp claim is unavailable"
    )


class EnvironmentJwtTokenIssuer:
    """
    Adapter over the canonical JWT issue and validation
    functions.

    The secret remains owned by secret_boundary.py and is
    never stored by this adapter.
    """

    async def issue_access_token(
        self,
        *,
        subject: str,
            extra_claims: Mapping[str, Any] | None = None,
) -> IssuedServiceToken:
        token = issue_access_token(
            subject,
                    extra_claims=extra_claims,
                )

        validated = validate_access_token(
            token
        )

        return IssuedServiceToken(
            token=token,
            token_id=_as_identifier(
                _claim_value(
                    validated,
                    "token_id",
                    "jti",
                )
            ),
            issued_at=_as_datetime(
                _claim_value(
                    validated,
                    "issued_at",
                    "iat",
                )
            ),
            expires_at=_as_datetime(
                _claim_value(
                    validated,
                    "expires_at",
                    "exp",
                )
            ),
        )

    async def issue_refresh_token(
        self,
        *,
        subject: str,
            extra_claims: Mapping[str, Any] | None = None,
) -> IssuedServiceToken:
        token = issue_refresh_token(
            subject,
                    extra_claims=extra_claims,
                )

        validated = validate_refresh_token(
            token
        )

        return IssuedServiceToken(
            token=token,
            token_id=_as_identifier(
                _claim_value(
                    validated,
                    "token_id",
                    "jti",
                )
            ),
            issued_at=_as_datetime(
                _claim_value(
                    validated,
                    "issued_at",
                    "iat",
                )
            ),
            expires_at=_as_datetime(
                _claim_value(
                    validated,
                    "expires_at",
                    "exp",
                )
            ),
        )


def build_authentication_runtime(
    session,
) -> tuple[
    RegistrationService,
    LoginService,
]:
    """
    Compose the canonical registration and login services.

    Construction validates the environment-only JWT secret
    and creates dependencies. It performs no repository
    query, database mutation, commit, rollback, or token
    issuance.
    """

    secret = load_jwt_secret()

    user_repository = IdentityUserRepository(
        session
    )

    refresh_repository = (
        RefreshSessionRepository(
            session
        )
    )

    token_issuer = (
        EnvironmentJwtTokenIssuer()
    )

    def runtime_refresh_token_hash(
        token: str,
    ) -> str:
        return hash_refresh_token(
            token,
            pepper=secret,
        )

    dummy_password_hash = hash_password(
        "neurovest-runtime-dummy-password"
    )

    registration_service = RegistrationService(
        user_repository=user_repository,
        hash_password=hash_password,
        commit=session.commit,
        rollback=session.rollback,
    )

    login_service = LoginService(
        user_repository=user_repository,
        refresh_session_repository=(
            refresh_repository
        ),
        verify_password=verify_password,
        token_issuer=token_issuer,
        hash_refresh_token=(
            runtime_refresh_token_hash
        ),
        dummy_password_hash=(
            dummy_password_hash
        ),
        commit=session.commit,
        rollback=session.rollback,
    )

    return (
        registration_service,
        login_service,
    )


@asynccontextmanager
async def authentication_runtime() -> AsyncIterator[
    tuple[
        RegistrationService,
        LoginService,
    ]
]:
    """
    Open one identity-auth database session and compose the
    frozen services.

    Entering the context creates no users or refresh
    sessions and performs no commit.
    """

    async with async_session() as session:
        yield build_authentication_runtime(
            session
        )


def build_session_lifecycle_runtime(
    session,
) -> SessionLifecycleService:
    secret = load_jwt_secret()

    user_repository = IdentityUserRepository(
        session
    )

    refresh_repository = (
        RefreshSessionRepository(
            session
        )
    )

    refresh_service = RefreshSessionService(
        session
    )

    token_issuer = EnvironmentJwtTokenIssuer()

    def runtime_validate_refresh_token(
        token: str,
    ) -> ValidatedRefreshIdentity:
        validated = validate_refresh_token(
            token
        )

        return ValidatedRefreshIdentity(
            subject=_as_identifier(
                _claim_value(
                    validated,
                    "subject",
                    "sub",
                )
            ),
            token_id=_as_identifier(
                _claim_value(
                    validated,
                    "token_id",
                    "jti",
                )
            ),
        )

    def runtime_hash_refresh_token(
        token: str,
    ) -> str:
        return hash_refresh_token(
            token,
            pepper=secret,
        )

    def runtime_verify_refresh_token(
        token: str,
        expected_hash: str,
    ) -> bool:
        return verify_refresh_token_hash(
            token,
            expected_hash,
            pepper=secret,
        )

    return SessionLifecycleService(
        refresh_repository=refresh_repository,
        refresh_service=refresh_service,
        token_issuer=token_issuer,
        validate_refresh_token=(
            runtime_validate_refresh_token
        ),
        hash_refresh_token=(
            runtime_hash_refresh_token
        ),
        verify_refresh_token=(
            runtime_verify_refresh_token
        ),
        commit=session.commit,
        rollback=session.rollback,
        access_revocation_repository=(
            AccessTokenRevocationRepository(
                session
            )
        ),
               user_repository=user_repository,
           )


@asynccontextmanager
async def session_lifecycle_runtime() -> AsyncIterator[
    SessionLifecycleService
]:
    async with async_session() as session:
        yield build_session_lifecycle_runtime(
            session
        )
