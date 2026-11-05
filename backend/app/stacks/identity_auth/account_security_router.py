
"""
F12-R3E staged authenticated account management.

Not mounted or deployed. This module is a candidate for
review, security testing and explicit route registration.

The password operation revokes refresh sessions atomically.
Access-token revocation must be qualified separately.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy import select, update

from backend.app.stacks.db_runtime.database import async_session
from backend.app.stacks.identity_auth.api_dependencies import (
    require_authenticated_principal,
)
from backend.app.stacks.identity_auth.models import (
    IdentityUser,
    IdentityRefreshSession,
)
from backend.app.stacks.identity_auth.credential_generation import (
    increment_generation,
)

from backend.app.stacks.identity_auth.passwords import (
    hash_password,
    verify_password,
)
from backend.app.stacks.identity_auth.password_change_service import (
    validate_replacement_password,
)

router = APIRouter(
    prefix="/api/v1/account",
    tags=["account"],
)


def normalized_display_name(value):
    if value is None:
        return None

    if not isinstance(value, str):
        raise ValueError("Invalid display name")

    value = value.strip()

    if len(value) > 100:
        raise ValueError("Display name too long")

    if any(ord(c) < 32 or ord(c) == 127 for c in value):
        raise ValueError("Invalid display name")

    return value or None


def account_owner(principal):
    subject = getattr(principal, "subject", None)

    if not isinstance(subject, str) or not subject.strip():
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
        )

    return subject


async def active_owner(session, subject):
    result = await session.execute(
        select(IdentityUser).where(
            IdentityUser.id == subject
        )
    )

    user = result.scalars().one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="Account unavailable")

    if user.is_active is not True or user.status != "active":
        raise HTTPException(status_code=403, detail="Account unavailable")

    return user


def public_profile(user):
    return {
        "display_name": user.display_name,
        "email": user.email_normalized,
        "profile_editable_fields": ["display_name"],
    }


@router.get("/profile")
async def read_own_profile(
    principal=Depends(require_authenticated_principal),
):
    owner = account_owner(principal)

    async with async_session() as session:
        user = await active_owner(session, owner)
        return public_profile(user)


@router.patch("/profile")
async def update_own_profile(
    payload: dict = Body(...),
    principal=Depends(require_authenticated_principal),
):
    owner = account_owner(principal)

    if type(payload) is not dict or set(payload) != {"display_name"}:
        raise HTTPException(
            status_code=422,
            detail="Only display_name may be updated",
        )

    try:
        name = normalized_display_name(payload["display_name"])
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Invalid display name",
        ) from None

    async with async_session() as session:
        async with session.begin():
            user = await active_owner(session, owner)
            user.display_name = name

        return {
            "display_name": name,
            "email": user.email_normalized,
            "profile_editable_fields": ["display_name"],
        }


@router.post("/password")
async def change_own_password(
    payload: dict = Body(...),
    principal=Depends(require_authenticated_principal),
):
    owner = account_owner(principal)

    if type(payload) is not dict or set(payload) != {
        "current_password",
        "new_password",
    }:
        raise HTTPException(
            status_code=422,
            detail="Invalid password-change request",
        )

    current_password = payload["current_password"]
    new_password = payload["new_password"]

    if (
        not isinstance(current_password, str)
        or not isinstance(new_password, str)
        or not current_password
        or not new_password
        or len(current_password) > 4096
        or len(new_password) > 4096
    ):
        raise HTTPException(
            status_code=422,
            detail="Invalid password-change request",
        )

    if current_password == new_password:
        raise HTTPException(
            status_code=422,
            detail="Choose a different password",
        )

    try:
        validate_replacement_password(new_password)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="New password does not meet requirements",
        ) from None

    async with async_session() as session:
        async with session.begin():
            # Lock the account row against concurrent password updates.
            result = await session.execute(
                select(IdentityUser)
                .where(IdentityUser.id == owner)
                .with_for_update()
            )
            user = result.scalars().one_or_none()

            if (
                user is None
                or user.is_active is not True
                or user.status != "active"
            ):
                raise HTTPException(
                    status_code=403,
                    detail="Account unavailable",
                )

            # Forced-reset sessions must use their dedicated flow.
            if user.must_change_password:
                raise HTTPException(
                    status_code=403,
                    detail="Required password change must be completed",
                )

            if not verify_password(
                current_password,
                user.password_hash,
            ):
                raise HTTPException(
                    status_code=403,
                    detail="Current password is incorrect",
                )

            user.password_hash = hash_password(new_password)

            # Revocation belongs in the SAME transaction
            # as the password-hash update.
            await session.execute(
                update(IdentityRefreshSession)
                .where(
                    IdentityRefreshSession.user_id == owner,
                    IdentityRefreshSession.revoked_at.is_(None),
                )
                .values(revoked_at=datetime.now(timezone.utc))
            )

            # F12-R3P: invalidate previous credential generations
            # in the same transaction as the password update.
            await increment_generation(session, owner)

    # Never return credentials, hashes, or session identifiers.
    # Sign-in again using the new password.
    return {
        "status": "password_changed",
        "reauthentication_required": True,
    }
