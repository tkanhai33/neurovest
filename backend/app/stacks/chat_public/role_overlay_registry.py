from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from backend.app.stacks.identity_auth.authorization_policy import (
    AuthorizationRole,
    SubscriptionTier,
)


@dataclass(frozen=True)
class RoleOverlay:
    """
    Immutable conversational overlay.

    An overlay changes response framing only. It never grants permissions,
    bypasses authorization, enables tools, activates trading, or modifies
    subscription entitlements.
    """

    role: AuthorizationRole
    title: str
    instructions: tuple[str, ...]
    may_receive_repository_context: bool
    may_receive_architecture_context: bool
    may_receive_administrative_context: bool


@dataclass(frozen=True)
class SubscriptionOverlay:
    """
    Immutable subscription-context overlay.

    Subscription tiers describe product context only. They do not replace
    authorization roles and cannot grant administrative or developer access.
    """

    tier: SubscriptionTier
    title: str
    instructions: tuple[str, ...]


@dataclass(frozen=True)
class ResolvedRoleOverlay:
    role: AuthorizationRole
    subscription_tier: SubscriptionTier | None
    role_overlay: RoleOverlay
    subscription_overlay: SubscriptionOverlay | None
    source_role_value: str | None
    source_tier_value: str | None


_ROLE_OVERLAYS: Mapping[
    AuthorizationRole,
    RoleOverlay,
] = MappingProxyType(
    {
        AuthorizationRole.USER: RoleOverlay(
            role=AuthorizationRole.USER,
            title="Authenticated user",
            instructions=(
                "Address the user as an authenticated NeuroVest user.",
                "Explain financial and system concepts clearly without "
                "exposing internal administrative or developer-only details.",
                "Do not imply that subscription tier grants authorization.",
                "Keep live brokerage execution locked unless a separately "
                "authorized execution workflow explicitly proves otherwise.",
            ),
            may_receive_repository_context=False,
            may_receive_architecture_context=False,
            may_receive_administrative_context=False,
        ),
        AuthorizationRole.ADMIN: RoleOverlay(
            role=AuthorizationRole.ADMIN,
            title="Administrator",
            instructions=(
                "The authenticated principal has an administrative role.",
                "Administrative context may be discussed when it is present "
                "in supplied evidence.",
                "Do not expose secrets, credentials, raw tokens, passwords, "
                "or private user data.",
                "Do not treat administrative status as developer ownership "
                "or permission to bypass safety boundaries.",
            ),
            may_receive_repository_context=False,
            may_receive_architecture_context=True,
            may_receive_administrative_context=True,
        ),
        AuthorizationRole.DEVELOPER: RoleOverlay(
            role=AuthorizationRole.DEVELOPER,
            title="Developer",
            instructions=(
                "The authenticated principal has the canonical developer role.",
                "Repository, architecture, capability, qualification, and "
                "runtime evidence may be discussed when actually supplied.",
                "Clearly separate proven results, proposed changes, missing "
                "evidence, and unverified assumptions.",
                "Never claim that tests, tools, providers, migrations, broker "
                "operations, or repository changes occurred without evidence.",
                "Developer status does not bypass safety, execution locks, "
                "authorization checks, or truth boundaries.",
            ),
            may_receive_repository_context=True,
            may_receive_architecture_context=True,
            may_receive_administrative_context=True,
        ),
    }
)


def _build_subscription_overlays() -> Mapping[
    SubscriptionTier,
    SubscriptionOverlay,
]:
    overlays: dict[
        SubscriptionTier,
        SubscriptionOverlay,
    ] = {}

    for tier in SubscriptionTier:
        tier_value = str(tier.value)

        overlays[tier] = SubscriptionOverlay(
            tier=tier,
            title=f"{tier_value.replace('_', ' ').title()} tier",
            instructions=(
                f"The authenticated subscription tier is {tier_value!r}.",
                "Treat this as product-context information only.",
                "Do not infer tools, permissions, broker access, market-data "
                "access, or administrative authority from the tier alone.",
                "Only describe tier-specific capabilities when corresponding "
                "capability or entitlement evidence is supplied.",
            ),
        )

    return MappingProxyType(overlays)


_SUBSCRIPTION_OVERLAYS = _build_subscription_overlays()


_ROLE_ALIASES: Mapping[str, AuthorizationRole] = MappingProxyType(
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


def _clean_value(
    value: Any,
) -> str | None:
    if value is None:
        return None

    raw = getattr(
        value,
        "value",
        value,
    )

    text = str(raw).strip().lower()

    return text or None


def normalize_overlay_role(
    value: Any,
) -> AuthorizationRole:
    """
    Normalize role context conservatively.

    Unknown or missing values fall back to USER. A malformed claim must never
    elevate a principal to admin or developer behavior.
    """

    if isinstance(value, AuthorizationRole):
        return value

    normalized = _clean_value(value)

    if normalized is None:
        return AuthorizationRole.USER

    return _ROLE_ALIASES.get(
        normalized,
        AuthorizationRole.USER,
    )


def normalize_overlay_tier(
    value: Any,
) -> SubscriptionTier | None:
    if isinstance(value, SubscriptionTier):
        return value

    normalized = _clean_value(value)

    if normalized is None:
        return None

    try:
        return SubscriptionTier(normalized)
    except ValueError:
        return None


def _first_claim(
    claims: Mapping[str, Any],
    names: tuple[str, ...],
) -> Any:
    for name in names:
        if name in claims:
            return claims[name]

    return None


def resolve_role_overlay(
    *,
    role: Any = None,
    subscription_tier: Any = None,
) -> ResolvedRoleOverlay:
    normalized_role = normalize_overlay_role(
        role
    )

    normalized_tier = normalize_overlay_tier(
        subscription_tier
    )

    return ResolvedRoleOverlay(
        role=normalized_role,
        subscription_tier=normalized_tier,
        role_overlay=_ROLE_OVERLAYS[
            normalized_role
        ],
        subscription_overlay=(
            _SUBSCRIPTION_OVERLAYS.get(
                normalized_tier
            )
            if normalized_tier is not None
            else None
        ),
        source_role_value=_clean_value(role),
        source_tier_value=_clean_value(
            subscription_tier
        ),
    )


def resolve_principal_overlay(
    principal: Any,
) -> ResolvedRoleOverlay:
    """
    Resolve an overlay from an AuthenticatedPrincipal-compatible object.

    Only the claims mapping is read. No authentication or authorization
    decision is made here.
    """

    claims = getattr(
        principal,
        "claims",
        {},
    )

    if not isinstance(claims, Mapping):
        claims = {}

    role = _first_claim(
        claims,
        (
            "authorization_role",
            "role",
            "user_role",
        ),
    )

    tier = _first_claim(
        claims,
        (
            "subscription_tier",
            "tier",
            "plan",
        ),
    )

    return resolve_role_overlay(
        role=role,
        subscription_tier=tier,
    )


def render_role_overlay(
    resolved: ResolvedRoleOverlay,
) -> str:
    lines = [
        "ROLE OVERLAY",
        f"Authorization role: {resolved.role.value}",
        f"Role title: {resolved.role_overlay.title}",
        (
            "Subscription tier: "
            + (
                str(
                    resolved.subscription_tier.value
                )
                if resolved.subscription_tier
                is not None
                else "unknown"
            )
        ),
        (
            "Repository context permitted: "
            f"{resolved.role_overlay.may_receive_repository_context}"
        ),
        (
            "Architecture context permitted: "
            f"{resolved.role_overlay.may_receive_architecture_context}"
        ),
        (
            "Administrative context permitted: "
            f"{resolved.role_overlay.may_receive_administrative_context}"
        ),
        "Role instructions:",
    ]

    lines.extend(
        f"- {instruction}"
        for instruction
        in resolved.role_overlay.instructions
    )

    if resolved.subscription_overlay is not None:
        lines.append(
            "Subscription instructions:"
        )

        lines.extend(
            f"- {instruction}"
            for instruction
            in resolved.subscription_overlay.instructions
        )

    lines.extend(
        (
            "Boundary:",
            "- This overlay affects conversational framing only.",
            "- It does not grant permissions, execute tools, enable trading, "
            "or override authorization and safety controls.",
        )
    )

    return "\n".join(lines)


def role_overlays() -> Mapping[
    AuthorizationRole,
    RoleOverlay,
]:
    return _ROLE_OVERLAYS


def subscription_overlays() -> Mapping[
    SubscriptionTier,
    SubscriptionOverlay,
]:
    return _SUBSCRIPTION_OVERLAYS


__all__ = [
    "ResolvedRoleOverlay",
    "RoleOverlay",
    "SubscriptionOverlay",
    "normalize_overlay_role",
    "normalize_overlay_tier",
    "render_role_overlay",
    "resolve_principal_overlay",
    "resolve_role_overlay",
    "role_overlays",
    "subscription_overlays",
]
