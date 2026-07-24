from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType


class AuthorizationRole(StrEnum):
    USER = "user"
    ADMIN = "admin"
    DEVELOPER = "developer"


class SubscriptionTier(StrEnum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ELITE = "elite"
    ENTERPRISE = "enterprise"
    INTERNAL = "internal"


ROLE_ALIASES = MappingProxyType(
    {
        "user": AuthorizationRole.USER,
        "admin": AuthorizationRole.ADMIN,
        "administrator": AuthorizationRole.ADMIN,
        "system_admin": AuthorizationRole.ADMIN,
        "developer": AuthorizationRole.DEVELOPER,
        "dev": AuthorizationRole.DEVELOPER,
        "owner": AuthorizationRole.DEVELOPER,
    }
)


USER_PERMISSIONS = frozenset(
    {
        "profile.read.self",
        "profile.update.self",
        "portfolio.read.self",
        "portfolio.update.self",
        "journal.read.self",
        "journal.write.self",
        "chat.use",
        "broker.paper",
    }
)


ADMIN_PERMISSIONS = frozenset(
    {
        "users.read",
        "users.require_password_reset",
        "users.issue_temporary_password",
        "users.disable",
        "users.enable",
        "users.delete",
        "sessions.read",
        "sessions.revoke",
        "audit.read",
        "audit.export",
        "runtime.read",
        "support.manage",
    }
)


DEVELOPER_PERMISSIONS = frozenset(
    ADMIN_PERMISSIONS
    | {
        "runtime.control",
        "developer.debug",
        "developer.iqc",
        "developer.feature_flags",
        "developer.diagnostics",
    }
)


ROLE_PERMISSIONS = MappingProxyType(
    {
        AuthorizationRole.USER: USER_PERMISSIONS,
        AuthorizationRole.ADMIN: ADMIN_PERMISSIONS,
        AuthorizationRole.DEVELOPER: DEVELOPER_PERMISSIONS,
    }
)


ADMINISTRATIVE_ROLES = frozenset(
    {
        AuthorizationRole.ADMIN,
        AuthorizationRole.DEVELOPER,
    }
)


EXPLICITLY_SEPARATE_PERMISSIONS = frozenset(
    {
        "broker.live",
        "production.keys.manage",
        "emergency_stop.control",
    }
)


@dataclass(
    frozen=True,
    slots=True,
)
class AuthorizationDecision:
    allowed: bool
    normalized_role: AuthorizationRole | None
    required_permissions: frozenset[str]
    granted_permissions: frozenset[str]
    missing_permissions: frozenset[str]
    reason: str


def normalize_role(
    value: object,
) -> AuthorizationRole | None:
    if isinstance(value, AuthorizationRole):
        return value

    if not isinstance(value, str):
        return None

    normalized = value.strip().lower()

    if not normalized:
        return None

    return ROLE_ALIASES.get(normalized)


def canonical_role_value(
    value: object,
) -> str | None:
    role = normalize_role(value)

    return (
        role.value
        if role is not None
        else None
    )


def normalize_subscription_tier(
    value: object,
) -> SubscriptionTier | None:
    if isinstance(value, SubscriptionTier):
        return value

    if not isinstance(value, str):
        return None

    normalized = value.strip().lower()

    if not normalized:
        return None

    try:
        return SubscriptionTier(normalized)
    except ValueError:
        return None


def permissions_for_role(
    value: object,
) -> frozenset[str]:
    role = normalize_role(value)

    if role is None:
        return frozenset()

    return ROLE_PERMISSIONS.get(
        role,
        frozenset(),
    )


def is_administrative_role(
    value: object,
) -> bool:
    role = normalize_role(value)

    return role in ADMINISTRATIVE_ROLES


def has_permission(
    role: object,
    permission: object,
) -> bool:
    if not isinstance(permission, str):
        return False

    normalized = permission.strip()

    if not normalized:
        return False

    if normalized in EXPLICITLY_SEPARATE_PERMISSIONS:
        return False

    return normalized in permissions_for_role(role)


def has_all_permissions(
    role: object,
    permissions: Iterable[object],
) -> bool:
    requested: list[str] = []

    for permission in permissions:
        if not isinstance(permission, str):
            return False

        normalized = permission.strip()

        if not normalized:
            return False

        requested.append(normalized)

    return all(
        has_permission(role, permission)
        for permission in requested
    )


def authorize(
    role: object,
    required_permissions: Iterable[object],
) -> AuthorizationDecision:
    normalized_role = normalize_role(role)
    required: set[str] = set()

    for permission in required_permissions:
        if not isinstance(permission, str):
            return AuthorizationDecision(
                allowed=False,
                normalized_role=normalized_role,
                required_permissions=frozenset(),
                granted_permissions=permissions_for_role(role),
                missing_permissions=frozenset(),
                reason="Permission value is invalid",
            )

        normalized = permission.strip()

        if not normalized:
            return AuthorizationDecision(
                allowed=False,
                normalized_role=normalized_role,
                required_permissions=frozenset(),
                granted_permissions=permissions_for_role(role),
                missing_permissions=frozenset(),
                reason="Permission value is empty",
            )

        required.add(normalized)

    required_permissions_frozen = frozenset(required)
    granted = permissions_for_role(role)

    missing = frozenset(
        permission
        for permission in required_permissions_frozen
        if not has_permission(role, permission)
    )

    allowed = (
        normalized_role is not None
        and not missing
    )

    if normalized_role is None:
        reason = "Role is unrecognized"
    elif missing:
        reason = "Required permissions are missing"
    else:
        reason = "Authorization granted"

    return AuthorizationDecision(
        allowed=allowed,
        normalized_role=normalized_role,
        required_permissions=required_permissions_frozen,
        granted_permissions=granted,
        missing_permissions=missing,
        reason=reason,
    )
