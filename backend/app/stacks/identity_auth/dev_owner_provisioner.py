from __future__ import annotations

from dataclasses import dataclass

from backend.app.stacks.db_runtime.database import (
    async_session,
    engine,
)

from backend.app.stacks.identity_auth.passwords import (
    hash_password,
    verify_password,
)

from backend.app.stacks.identity_auth.repositories import (
    IdentityUserRepository,
)


DEV_OWNER_EMAIL = "dev@neurovest.com"
DEV_OWNER_TEMPORARY_PASSWORD = "pass123"
DEV_OWNER_ROLE = "owner"


@dataclass(
    frozen=True,
    slots=True,
)
class DevOwnerProvisioningResult:
    user_id: str
    email: str
    role: str
    must_change_password: bool
    created: bool
    temporary_password_valid: bool


async def provision_dev_owner() -> DevOwnerProvisioningResult:
    async with async_session() as session:
        repository = IdentityUserRepository(
            session
        )

        user = await repository.get_by_email(
            DEV_OWNER_EMAIL
        )

        created = user is None

        if user is None:
            user = await repository.create(
                email=DEV_OWNER_EMAIL,
                password_hash=hash_password(
                    DEV_OWNER_TEMPORARY_PASSWORD
                ),
                role=DEV_OWNER_ROLE,
                must_change_password=True,
            )
        else:
            await repository.update_identity_security_state(
                user,
                role=DEV_OWNER_ROLE,
            )

            user.status = "active"
            user.is_active = True

            if user.must_change_password:
                if not verify_password(
                    DEV_OWNER_TEMPORARY_PASSWORD,
                    user.password_hash,
                ):
                    await repository.update_password_hash(
                        user,
                        password_hash=hash_password(
                            DEV_OWNER_TEMPORARY_PASSWORD
                        ),
                    )
            else:
                # A completed password replacement is never reset
                # by an idempotent stage rerun.
                pass

        await session.commit()
        await session.refresh(
            user
        )

        result = DevOwnerProvisioningResult(
            user_id=user.id,
            email=user.email_normalized,
            role=user.role,
            must_change_password=(
                user.must_change_password
            ),
            created=created,
            temporary_password_valid=verify_password(
                DEV_OWNER_TEMPORARY_PASSWORD,
                user.password_hash,
            ),
        )

    await engine.dispose()

    return result
