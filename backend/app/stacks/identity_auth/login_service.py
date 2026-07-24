from __future__ import annotations

from backend.app.stacks.identity_auth.authorization_policy import (
    canonical_role_value,
    normalize_subscription_tier,
)

from backend.app.stacks.identity_auth.normalization import (
    normalize_email,
)

from backend.app.stacks.identity_auth.repositories import (
    IdentityUserRepository,
    RefreshSessionRepository,
)

from backend.app.stacks.identity_auth.service_contracts import (
    AuthenticationRejectedError,
    AuthenticationTokenPair,
    LoginCommand,
    PasswordVerifyFunction,
    RefreshTokenHashFunction,
    ServiceTokenIssuer,
)


class LoginService:
    def __init__(
        self,
        *,
        user_repository: IdentityUserRepository,
        refresh_session_repository: RefreshSessionRepository,
        verify_password: PasswordVerifyFunction,
        token_issuer: ServiceTokenIssuer,
        hash_refresh_token: RefreshTokenHashFunction,
        dummy_password_hash: str,
        commit,
        rollback,
    ) -> None:
        if not dummy_password_hash:
            raise ValueError(
                "A dummy password hash is required"
            )

        self._user_repository = (
            user_repository
        )

        self._refresh_session_repository = (
            refresh_session_repository
        )

        self._verify_password = (
            verify_password
        )

        self._token_issuer = (
            token_issuer
        )

        self._hash_refresh_token = (
            hash_refresh_token
        )

        self._dummy_password_hash = (
            dummy_password_hash
        )

        self._commit = commit
        self._rollback = rollback

    async def login(
        self,
        command: LoginCommand,
    ) -> AuthenticationTokenPair:
        try:
            normalized_email = (
                normalize_email(
                    command.email
                )
            )

            if not isinstance(
                command.password,
                str,
            ) or not command.password:
                await self._perform_dummy_verification(
                    command.password
                    if isinstance(
                        command.password,
                        str,
                    )
                    else ""
                )

                raise AuthenticationRejectedError(
                    "Authentication failed"
                )

            user = (
                await self._user_repository.get_by_email(
                    normalized_email
                )
            )

            stored_hash = (
                user.password_hash
                if user is not None
                else self._dummy_password_hash
            )

            password_valid = (
                self._verify_password(
                    command.password,
                    stored_hash,
                )
            )

            account_valid = (
                user is not None
                and user.is_active is True
                and user.status == "active"
            )

            if not (
                password_valid
                and account_valid
            ):
                raise AuthenticationRejectedError(
                    "Authentication failed"
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
                raise AuthenticationRejectedError(
                    "Authentication failed"
                )

            access_token = (
                await self._token_issuer.issue_access_token(
                    subject=user.id,
                    extra_claims={
                        "authorization_role": canonical_role,
                        "subscription_tier": canonical_tier.value,
                    },
                )
            )

            refresh_token = (
                await self._token_issuer.issue_refresh_token(
                    subject=user.id,
                          extra_claims={
                              "authorization_role": canonical_role,
                              "subscription_tier": canonical_tier.value,
                          },
                      )
            )

            if (
                access_token.token
                == refresh_token.token
            ):
                raise AuthenticationRejectedError(
                    "Authentication failed"
                )

            refresh_token_hash = (
                self._hash_refresh_token(
                    refresh_token.token
                )
            )

            if not refresh_token_hash:
                raise AuthenticationRejectedError(
                    "Authentication failed"
                )

            await self._refresh_session_repository.create(
                user_id=user.id,
                token_id=refresh_token.token_id,
                token_hash=refresh_token_hash,
                issued_at=refresh_token.issued_at,
                expires_at=refresh_token.expires_at,
            )

            await self._commit()

            return AuthenticationTokenPair(
                access_token=access_token.token,
                refresh_token=refresh_token.token,
                token_type="bearer",
                access_expires_at=(
                    access_token.expires_at
                ),
                refresh_expires_at=(
                    refresh_token.expires_at
                ),
                password_change_required=bool(
                    getattr(
                        user,
                        "must_change_password",
                        False,
                    )
                ),
            )

        except AuthenticationRejectedError:
            await self._rollback()

            raise

        except Exception as exc:
            await self._rollback()

            raise AuthenticationRejectedError(
                "Authentication failed"
            ) from exc

    async def _perform_dummy_verification(
        self,
        password: str,
    ) -> None:
        self._verify_password(
            password,
            self._dummy_password_hash,
        )
