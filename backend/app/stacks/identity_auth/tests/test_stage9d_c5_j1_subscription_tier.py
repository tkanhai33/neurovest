from __future__ import annotations

from sqlalchemy import CheckConstraint

from backend.app.stacks.identity_auth.authorization_policy import (
    AuthorizationRole,
    SubscriptionTier,
    has_permission,
    normalize_subscription_tier,
)
from backend.app.stacks.identity_auth.models import (
    IdentityUser,
)


def test_subscription_tier_policy_values_are_exact() -> None:
    assert {
        tier.value
        for tier in SubscriptionTier
    } == {
        "free",
        "basic",
        "pro",
        "elite",
        "enterprise",
        "internal",
    }


def test_unknown_subscription_tier_fails_closed() -> None:
    assert normalize_subscription_tier(
        "unknown"
    ) is None

    assert normalize_subscription_tier(
        ""
    ) is None

    assert normalize_subscription_tier(
        None
    ) is None


def test_identity_user_subscription_tier_model_contract() -> None:
    column = IdentityUser.__table__.columns[
        "subscription_tier"
    ]

    assert str(column.type) == "VARCHAR(32)"
    assert column.nullable is False
    assert column.default is not None
    assert column.server_default is not None


def test_identity_user_subscription_constraint_exists() -> None:
    constraints = {
        constraint.name: constraint
        for constraint in IdentityUser.__table__.constraints
        if isinstance(
            constraint,
            CheckConstraint,
        )
    }

    assert (
        "ck_identity_users_subscription_tier"
        in constraints
    )


def test_role_and_tier_remain_separate() -> None:
    assert (
        IdentityUser.__table__.columns["role"]
        is not
        IdentityUser.__table__.columns[
            "subscription_tier"
        ]
    )

    assert AuthorizationRole.USER.value == "user"
    assert SubscriptionTier.FREE.value == "free"


def test_no_tier_grants_broker_live() -> None:
    for tier in SubscriptionTier:
        assert tier.value not in {
            role.value
            for role in AuthorizationRole
        }

    for role in (
        "user",
        "admin",
        "developer",
        "owner",
    ):
        assert not has_permission(
            role,
            "broker.live",
        )
