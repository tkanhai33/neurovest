from __future__ import annotations

from backend.app.stacks.identity_auth.normalization import (
    normalize_email,
)

from backend.app.stacks.identity_auth.repositories import (
    IdentityUserRepository,
)

from backend.app.stacks.identity_auth.service_contracts import (
    PasswordHashFunction,
    RegisteredIdentity,
    RegistrationCommand,
    RegistrationRejectedError,
)


class RegistrationService:
    def __init__(
        self,
        *,
        user_repository: IdentityUserRepository,
        hash_password: PasswordHashFunction,
        commit,
        rollback,
    ) -> None:
        self._user_repository = (
            user_repository
        )

        self._hash_password = (
            hash_password
        )

        self._commit = commit
        self._rollback = rollback

    async def register(
        self,
        command: RegistrationCommand,
    ) -> RegisteredIdentity:
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
                raise RegistrationRejectedError(
                    "Registration could not be completed"
                )

            existing = (
                await self._user_repository.get_by_email(
                    normalized_email
                )
            )

            if existing is not None:
                raise RegistrationRejectedError(
                    "Registration could not be completed"
                )

            password_hash = (
                self._hash_password(
                    command.password
                )
            )

            if not isinstance(
                password_hash,
                str,
            ) or not password_hash:
                raise RegistrationRejectedError(
                    "Registration could not be completed"
                )

            # Validate display_name if provided
            if command.display_name is not None:
                display_name = command.display_name.strip()
                if not display_name:
                    raise RegistrationRejectedError(
                        "Display name cannot be blank"
                    )
                if len(display_name) > 100:
                    raise RegistrationRejectedError(
                        "Display name exceeds maximum length of 100 characters"
                    )
            else:
                display_name = None

            user = await self._user_repository.create(
                email=normalized_email,
                password_hash=password_hash,
                display_name=display_name,
            )

            await self._commit()

            return RegisteredIdentity(
                user_id=user.id,
                email_normalized=(
                    user.email_normalized
                ),
                status=user.status,
            )

        except RegistrationRejectedError:
            await self._rollback()

            raise

        except Exception as exc:
            await self._rollback()

            raise RegistrationRejectedError(
                "Registration could not be completed"
            ) from exc
