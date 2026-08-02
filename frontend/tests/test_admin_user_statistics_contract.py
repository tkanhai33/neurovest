from pathlib import Path


BACKEND = Path(
    "backend/app/main.py"
)

PROXY = Path(
    "frontend/app/api/admin/user-stats/route.ts"
)

PAGE = Path(
    "frontend/app/admin/user-stats/page.tsx"
)


def test_backend_exposes_admin_statistics_route() -> None:
    source = BACKEND.read_text(
        encoding="utf-8",
    )

    assert (
        '"/api/v1/admin/user-stats"'
        in source
    )

    assert (
        "get_administrative_user_statistics"
        in source
    )

    assert (
        "_require_admin_statistics_principal"
        in source
    )


def test_statistics_use_proven_database_tables() -> None:
    source = BACKEND.read_text(
        encoding="utf-8",
    )

    for table in (
        "identity_users",
        "identity_refresh_sessions",
        "order_history",
        "portfolio_inventory",
        "snaptrade_user_credentials",
    ):
        assert table in source


def test_active_sessions_are_expiry_and_revocation_aware() -> None:
    source = BACKEND.read_text(
        encoding="utf-8",
    )

    assert "revoked_at IS NULL" in source
    assert "expires_at > :now" in source


def test_statistics_remain_admin_only() -> None:
    source = BACKEND.read_text(
        encoding="utf-8",
    )

    assert "Administrative statistics access denied" in source
    assert "status_code=403" in source
    assert "administrative_roles" in source


def test_broker_stat_is_owner_distinct() -> None:
    source = BACKEND.read_text(
        encoding="utf-8",
    )

    assert (
        "DISTINCT neurovest_user_id"
        in source
    )


def test_revenue_is_not_fabricated() -> None:
    source = BACKEND.read_text(
        encoding="utf-8",
    )

    assert '"configured": False' in source
    assert '"monthly_revenue": None' in source
    assert "Billing not configured" in source


def test_live_execution_remains_disabled() -> None:
    source = BACKEND.read_text(
        encoding="utf-8",
    )

    assert (
        '"live_execution_enabled":'
        in source
    )

    assert (
        '"live_broker_trading": False'
        in source
    )


def test_frontend_proxy_forwards_admin_statistics() -> None:
    source = PROXY.read_text(
        encoding="utf-8",
    )

    assert "backendFetch(" in source

    assert (
        '"/api/v1/admin/user-stats"'
        in source
    )

    assert (
        'export async function GET()'
        in source
    )


def test_user_statistics_page_is_live() -> None:
    source = PAGE.read_text(
        encoding="utf-8",
    )

    assert '"use client"' in source
    assert '"/api/admin/user-stats"' in source
    assert "Registered users" in source
    assert "Active sessions" in source
    assert "Broker registered" in source
    assert "Monthly revenue" in source
    assert "Refresh statistics" in source


def test_placeholder_api_binding_is_removed() -> None:
    source = PAGE.read_text(
        encoding="utf-8",
    )

    assert "API binding pending" not in source
    assert 'value="—"' not in source


def test_statistics_uses_canonical_principal_role_first() -> None:
    source = BACKEND.read_text(
        encoding="utf-8",
    )

    assert (
        'getattr(\n'
        '            principal,\n'
        '            "role",'
        in source
    )

    assert (
        'getattr(\n'
        '            principal,\n'
        '            "authorization_role",'
        in source
    )

    assert "direct_role" in source
    assert "claim_role" in source

    assert (
        "direct_role\n"
        "        or claim_role"
        in source
    )


def test_developer_and_owner_roles_are_administrative() -> None:
    source = BACKEND.read_text(
        encoding="utf-8",
    )

    assert '"developer"' in source
    assert '"owner"' in source

