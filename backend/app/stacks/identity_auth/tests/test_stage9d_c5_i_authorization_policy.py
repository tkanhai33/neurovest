from backend.app.stacks.identity_auth.authorization_policy import (
    ADMINISTRATIVE_ROLES,
    AuthorizationRole,
    SubscriptionTier,
    authorize,
    canonical_role_value,
    has_all_permissions,
    has_permission,
    is_administrative_role,
    normalize_role,
    normalize_subscription_tier,
    permissions_for_role,
)


def test_canonical_roles() -> None:
    assert {
        role.value
        for role in AuthorizationRole
    } == {
        "user",
        "admin",
        "developer",
    }


def test_subscription_tiers_remain_separate() -> None:
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

    assert normalize_subscription_tier(
        "pro"
    ) is SubscriptionTier.PRO

    assert normalize_subscription_tier(
        "unknown"
    ) is None


def test_owner_normalizes_to_developer() -> None:
    assert normalize_role(
        "owner"
    ) is AuthorizationRole.DEVELOPER

    assert canonical_role_value(
        "owner"
    ) == "developer"


def test_administrative_roles() -> None:
    assert AuthorizationRole.ADMIN in ADMINISTRATIVE_ROLES
    assert AuthorizationRole.DEVELOPER in ADMINISTRATIVE_ROLES

    assert is_administrative_role("admin")
    assert is_administrative_role("developer")
    assert is_administrative_role("owner")
    assert not is_administrative_role("user")


def test_unknown_roles_fail_closed() -> None:
    for role in (
        None,
        "",
        "unknown",
        object(),
        42,
    ):
        assert normalize_role(role) is None
        assert permissions_for_role(role) == frozenset()
        assert not has_permission(role, "users.read")


def test_admin_user_management_permissions() -> None:
    assert has_all_permissions(
        "admin",
        {
            "users.read",
            "users.require_password_reset",
            "users.issue_temporary_password",
            "users.disable",
            "users.enable",
            "users.delete",
        },
    )


def test_developer_inherits_admin_permissions() -> None:
    assert has_all_permissions(
        "developer",
        {
            "users.read",
            "users.delete",
            "audit.read",
            "runtime.read",
            "runtime.control",
            "developer.iqc",
        },
    )


def test_dangerous_permissions_remain_separate() -> None:
    for role in (
        "user",
        "admin",
        "developer",
        "owner",
    ):
        assert not has_permission(role, "broker.live")
        assert not has_permission(role, "production.keys.manage")
        assert not has_permission(role, "emergency_stop.control")


def test_authorization_decisions_fail_closed() -> None:
    denied_unknown = authorize(
        "unknown",
        {"users.read"},
    )

    assert denied_unknown.allowed is False
    assert denied_unknown.normalized_role is None

    denied_user = authorize(
        "user",
        {"users.read"},
    )

    assert denied_user.allowed is False
    assert denied_user.missing_permissions == frozenset(
        {"users.read"}
    )

    allowed_admin = authorize(
        "admin",
        {
            "users.read",
            "users.disable",
        },
    )

    assert allowed_admin.allowed is True
    assert allowed_admin.missing_permissions == frozenset()
