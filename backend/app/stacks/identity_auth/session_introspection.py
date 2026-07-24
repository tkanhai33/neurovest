from __future__ import annotations

from typing import Any, Dict

from fastapi import HTTPException, status

from backend.app.stacks.identity_auth.authorization_policy import (
    canonical_role_value,
    normalize_subscription_tier,
    permissions_for_role,
)
from backend.app.stacks.identity_auth.models import IdentityUser
from backend.app.stacks.identity_auth.repositories import IdentityUserRepository


async def get_session_introspection(
    user_id: str, session_repo: IdentityUserRepository
) -> Dict[str, Any]:
    user = await session_repo.get_by_id(user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    if not user.is_active or user.status != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    role = canonical_role_value(user.role)
    subscription_tier = normalize_subscription_tier(user.subscription_tier)

    if role is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    if subscription_tier is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    permissions = permissions_for_role(role)
    is_administrative = any(
        perm in permissions for perm in ("admin", "administrator", "system_admin")
    )

    return {
        "user_id": user.id,
        "role": role,
        "subscription_tier": subscription_tier,
        "permissions": list(permissions),
        "is_administrative": is_administrative,
        "status": user.status,
        "is_active": user.is_active,
        "must_change_password": user.must_change_password,
        "display_name": user.display_name,
        "email": user.email_normalized,
    }
