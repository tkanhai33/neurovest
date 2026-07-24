from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import (
    Awaitable,
    Callable,
)

from backend.app.stacks.identity_auth.authorization_policy import (
    canonical_role_value,
    normalize_subscription_tier,
)

from backend.app.stacks.identity_auth.models import (
    IdentityRefreshSession,
)

from backend.app.stacks.identity_auth.repositories import (
    IdentityUserRepository,
    RefreshSessionRepository,
)

from backend.app.stacks.identity_auth.access_token_revocation_repository import (
    AccessTokenRevocationRepository,
)

from backend.app.stacks.identity_auth.service_contracts import (
    AuthenticationTokenPair,
    IssuedServiceToken,
    ServiceTokenIssuer,
)

from backend.app.stacks.identity_auth.session_service import (
    RefreshSessionExpiredError,
    RefreshSessionNotFoundError,
    RefreshSessionService,
    RefreshTokenReuseDetectedError,
)


class SessionLifecycleRejectedError(
    Exception
):
    """Generic fail-closed lifecycle rejection."""


@dataclass(frozen=True)
class ValidatedRefreshIdentity:
    subject: str
    token_id: str


RefreshTokenValidator = Callable[
    [
        str,
    ],
    ValidatedRefreshIdentity,
]


RefreshTokenHashFunction = Callable[
    [
        str,
    ],
    str,
]


RefreshTokenVerifyFunction = Callable[
    [
        str,
        str,
    ],
    bool,
]


CommitFunction = Callable[
    [],
    Awaitable[
        None
    ],
]


RollbackFunction = Callable[
    [],
    Awaitable[
        None
    ],
]


class SessionLifecycleService:
    def __init__(
        self,
        *,
        refresh_repository: RefreshSessionRepository,
        user_repository: IdentityUserRepository | None = None,
        refresh_service: RefreshSessionService,
        token_issuer: ServiceTokenIssuer,
        validate_refresh_token: RefreshTokenValidator,
        hash_refresh_token: RefreshTokenHashFunction,
        verify_refresh_token: RefreshTokenVerifyFunction,
        commit: CommitFunction,
        rollback: RollbackFunction,
        access_revocation_repository: (
            AccessTokenRevocationRepository
            | None
        ) = None,
    ) -> None:
        self._refresh_repository = (
            refresh_repository
        )

        self._user_repository = user_repository

        self._refresh_service = refresh_service

        self._token_issuer = token_issuer

        self._validate_refresh_token = (
            validate_refresh_token
        )

        self._hash_refresh_token = (
            hash_refresh_token
        )

        self._verify_refresh_token = (
            verify_refresh_token
        )

        self._commit = commit
        self._rollback = rollback
        self._access_revocation_repository = (
            access_revocation_repository
        )

    async def _validated_record(
        self,
        refresh_token: str,
    ) -> tuple[
        ValidatedRefreshIdentity,
        IdentityRefreshSession,
    ]:
        if not isinstance(
            refresh_token,
            str,
        ) or not refresh_token:
            raise SessionLifecycleRejectedError(
                "Session lifecycle request was rejected"
            )

        identity = self._validate_refresh_token(
            refresh_token
        )

        if (
            not identity.subject
            or not identity.token_id
        ):
            raise SessionLifecycleRejectedError(
                "Session lifecycle request was rejected"
            )

        record = (
            await self._refresh_repository.get_by_token_id(
                identity.token_id,
                for_update=True,
            )
        )

        if record is None:
            raise SessionLifecycleRejectedError(
                "Session lifecycle request was rejected"
            )

        if record.user_id != identity.subject:
            raise SessionLifecycleRejectedError(
                "Session lifecycle request was rejected"
            )

        if not self._verify_refresh_token(
            refresh_token,
            record.token_hash,
        ):
            raise SessionLifecycleRejectedError(
                "Session lifecycle request was rejected"
            )

        return (
            identity,
            record,
        )

    async def refresh(
        self,
        *,
        refresh_token: str,
    ) -> AuthenticationTokenPair:
        try:
            identity, _ = await self._validated_record(
                refresh_token
            )

            if self._user_repository is None:
                raise SessionLifecycleRejectedError(
                    "Session lifecycle request was rejected"
                )

            user = await self._user_repository.get_by_id(
                identity.subject
            )

            if (
                user is None
                or user.is_active is not True
                or user.status != "active"
            ):
                raise SessionLifecycleRejectedError(
                    "Session lifecycle request was rejected"
                )

            canonical_role = canonical_role_value(
                user.role
            )

            canonical_tier = normalize_subscription_tier(
                user.subscription_tier
            )

            if (
                canonical_role is None
                or canonical_tier is None
            ):
                raise SessionLifecycleRejectedError(
                    "Session lifecycle request was rejected"
                )

            access_token = (
                await self._token_issuer.issue_access_token(
                    subject=identity.subject,
                    extra_claims={
                        "authorization_role": canonical_role,
                        "subscription_tier": canonical_tier.value,
                    },
                )
            )

            replacement = (
                await self._token_issuer.issue_refresh_token(
                    subject=identity.subject,
                    extra_claims={
                        "authorization_role": canonical_role,
                        "subscription_tier": canonical_tier.value,
                    },
                )
            )

            if (
                access_token.token
                == replacement.token
            ):
                raise SessionLifecycleRejectedError(
                    "Session lifecycle request was rejected"
                )

            replacement_hash = (
                self._hash_refresh_token(
                    replacement.token
                )
            )

            if not replacement_hash:
                raise SessionLifecycleRejectedError(
                    "Session lifecycle request was rejected"
                )

            await self._refresh_service.rotate(
                current_token_id=identity.token_id,
                replacement_token_id=(
                    replacement.token_id
                ),
                replacement_token_hash=(
                    replacement_hash
                ),
                replacement_issued_at=(
                    replacement.issued_at
                ),
                replacement_expires_at=(
                    replacement.expires_at
                ),
            )

            await self._commit()

            return AuthenticationTokenPair(
                access_token=access_token.token,
                refresh_token=replacement.token,
                token_type="bearer",
                access_expires_at=(
                    access_token.expires_at
                ),
                refresh_expires_at=(
                    replacement.expires_at
                ),
            )

        except (
            RefreshTokenReuseDetectedError,
            RefreshSessionExpiredError,
        ) as exc:
            # Rotation intentionally changes durable state for
            # replay or expiry handling before raising.
            await self._commit()

            raise SessionLifecycleRejectedError(
                "Session lifecycle request was rejected"
            ) from exc

        except SessionLifecycleRejectedError:
            await self._rollback()

            raise

        except Exception as exc:
            await self._rollback()

            raise SessionLifecycleRejectedError(
                "Session lifecycle request was rejected"
            ) from exc

    async def logout(
        self,
        *,
        refresh_token: str,
        access_token_id: str | None = None,
        access_user_id: str | None = None,
        access_issued_at: datetime | None = None,
        access_expires_at: datetime | None = None,
    ) -> None:
        try:
            identity, _ = await self._validated_record(
                refresh_token
            )

            if access_token_id is not None:
                if (
                    self._access_revocation_repository
                    is None
                    or not access_user_id
                    or access_issued_at is None
                    or access_expires_at is None
                    or access_user_id
                    != identity.subject
                ):
                    raise SessionLifecycleRejectedError(
                        "Session lifecycle request was rejected"
                    )

                await (
                    self._access_revocation_repository
                    .revoke(
                        token_id=access_token_id,
                        user_id=access_user_id,
                        issued_at=access_issued_at,
                        expires_at=access_expires_at,
                        reason="logout",
                    )
                )

            await self._refresh_service.logout(
                token_id=identity.token_id
            )

            await self._commit()

        except SessionLifecycleRejectedError:
            await self._rollback()
            raise

        except Exception as exc:
            await self._rollback()

            raise SessionLifecycleRejectedError(
                "Session lifecycle request was rejected"
            ) from exc

    async def logout_all(
        self,
        *,
        user_id: str,
    ) -> int:
        try:
            if not isinstance(
                user_id,
                str,
            ) or not user_id:
                raise SessionLifecycleRejectedError(
                    "Session lifecycle request was rejected"
                )

            revoked = (
                await self._refresh_service.revoke_all(
                    user_id=user_id
                )
            )

            await self._commit()

            return revoked

        except SessionLifecycleRejectedError:
            await self._rollback()

            raise

        except Exception as exc:
            await self._rollback()

            raise SessionLifecycleRejectedError(
                "Session lifecycle request was rejected"
            ) from exc

    async def cleanup_expired(
        self,
        *,
        before: datetime | None = None,
    ) -> int:
        try:
            deleted = (
                await self._refresh_service.cleanup_expired(
                    before=before
                )
            )

            await self._commit()

            return deleted

        except Exception as exc:
            await self._rollback()

            raise SessionLifecycleRejectedError(
                "Session cleanup could not be completed"
            ) from exc
