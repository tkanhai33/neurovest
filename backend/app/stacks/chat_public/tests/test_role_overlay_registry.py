from __future__ import annotations

from dataclasses import FrozenInstanceError
from types import MappingProxyType

import pytest

from backend.app.stacks.chat_public.role_overlay_registry import (
    normalize_overlay_role,
    normalize_overlay_tier,
    render_role_overlay,
    resolve_principal_overlay,
    resolve_role_overlay,
    role_overlays,
    subscription_overlays,
)

from backend.app.stacks.identity_auth.authorization_policy import (
    AuthorizationRole,
    SubscriptionTier,
)

from backend.app.stacks.identity_auth.contracts import (
    AuthenticatedPrincipal,
)


def test_every_canonical_role_has_an_overlay() -> None:
    overlays = role_overlays()

    assert isinstance(
        overlays,
        MappingProxyType,
    )

    assert set(overlays) == set(
        AuthorizationRole
    )


def test_every_subscription_tier_has_an_overlay() -> None:
    overlays = subscription_overlays()

    assert isinstance(
        overlays,
        MappingProxyType,
    )

    assert set(overlays) == set(
        SubscriptionTier
    )


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("user", AuthorizationRole.USER),
        ("admin", AuthorizationRole.ADMIN),
        ("administrator", AuthorizationRole.ADMIN),
        ("system_admin", AuthorizationRole.ADMIN),
        ("developer", AuthorizationRole.DEVELOPER),
        ("dev", AuthorizationRole.DEVELOPER),
        ("owner", AuthorizationRole.DEVELOPER),
    ],
)
def test_role_aliases_use_canonical_roles(
    raw: str,
    expected: AuthorizationRole,
) -> None:
    assert normalize_overlay_role(raw) is expected


def test_unknown_role_fails_closed_to_user() -> None:
    assert (
        normalize_overlay_role(
            "superuser_from_untrusted_claim"
        )
        is AuthorizationRole.USER
    )

    assert (
        normalize_overlay_role(None)
        is AuthorizationRole.USER
    )


@pytest.mark.parametrize(
    "tier",
    list(SubscriptionTier),
)
def test_tier_normalization_uses_canonical_enum(
    tier: SubscriptionTier,
) -> None:
    assert (
        normalize_overlay_tier(
            tier.value
        )
        is tier
    )


def test_unknown_tier_does_not_invent_entitlement() -> None:
    assert (
        normalize_overlay_tier(
            "platinum_unlimited"
        )
        is None
    )


def test_principal_claims_resolve_role_and_tier() -> None:
    tier = next(
        iter(SubscriptionTier)
    )

    principal = AuthenticatedPrincipal(
        subject="stage4-user",
        token_id="stage4-token",
        claims={
            "role": "developer",
            "subscription_tier": tier.value,
        },
    )

    resolved = resolve_principal_overlay(
        principal
    )

    assert (
        resolved.role
        is AuthorizationRole.DEVELOPER
    )

    assert resolved.subscription_tier is tier

    assert (
        resolved.role_overlay
        .may_receive_repository_context
        is True
    )


def test_missing_claims_fail_closed_to_user() -> None:
    principal = AuthenticatedPrincipal(
        subject="stage4-user",
        token_id="stage4-token",
        claims={},
    )

    resolved = resolve_principal_overlay(
        principal
    )

    assert (
        resolved.role
        is AuthorizationRole.USER
    )

    assert resolved.subscription_tier is None


def test_overlay_is_conversational_not_authoritative() -> None:
    resolved = resolve_role_overlay(
        role="developer",
    )

    text = render_role_overlay(
        resolved
    )

    assert "ROLE OVERLAY" in text
    assert "Authorization role: developer" in text
    assert (
        "affects conversational framing only"
        in text
    )
    assert "does not grant permissions" in text
    assert "enable trading" in text


def test_overlay_models_are_immutable() -> None:
    resolved = resolve_role_overlay(
        role="user",
    )

    with pytest.raises(
        FrozenInstanceError,
    ):
        resolved.role = (  # type: ignore[misc]
            AuthorizationRole.ADMIN
        )


def test_role_overlay_registry_is_immutable() -> None:
    overlays = role_overlays()

    with pytest.raises(
        TypeError,
    ):
        overlays[
            AuthorizationRole.USER
        ] = overlays[  # type: ignore[index]
            AuthorizationRole.ADMIN
        ]


def test_admin_does_not_receive_repository_context() -> None:
    resolved = resolve_role_overlay(
        role="admin",
    )

    assert (
        resolved.role_overlay
        .may_receive_administrative_context
        is True
    )

    assert (
        resolved.role_overlay
        .may_receive_repository_context
        is False
    )


def test_owner_alias_resolves_to_developer_not_new_role() -> None:
    resolved = resolve_role_overlay(
        role="owner",
    )

    assert (
        resolved.role
        is AuthorizationRole.DEVELOPER
    )

    assert resolved.source_role_value == "owner"
