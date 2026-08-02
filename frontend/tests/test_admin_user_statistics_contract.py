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
        "require_administrative_principal"
        in source
    )

    assert (
        "AdministrativePrincipal"
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

    assert (
        "principal: AdministrativePrincipal = Depends("
        in source
    )

    assert (
        "require_administrative_principal"
        in source
    )

    assert (
        "require_authenticated_principal"
        not in source[
            source.index(
                "async def get_administrative_user_statistics("
            ):
            source.index(
                "# END ADMIN USER STATISTICS ENDPOINT"
            )
        ]
    )

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
    assert "Customer accounts" in source
    assert "Database identities" in source
    assert "Qualification / test identities" in source
    assert "Internal accounts" in source
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
        "from backend.app.stacks.identity_auth."
        "admin_read_dependencies import ("
        in source
    )

    assert (
        "AdministrativePrincipal,"
        in source
    )

    assert (
        "require_administrative_principal,"
        in source
    )

    assert (
        "def _require_admin_statistics_principal"
        not in source
    )

def test_developer_and_owner_roles_are_administrative() -> None:
    policy = Path(
        "backend/app/stacks/identity_auth/"
        "authorization_policy.py"
    ).read_text(
        encoding="utf-8",
    )

    assert (
        '"developer": AuthorizationRole.DEVELOPER'
        in policy
    )

    assert (
        '"owner": AuthorizationRole.DEVELOPER'
        in policy
    )

    assert (
        "AuthorizationRole.DEVELOPER,"
        in policy
    )

def test_admin_statistics_uses_canonical_administrative_dependency() -> None:
    source = BACKEND.read_text(
        encoding="utf-8",
    )

    assert (
        "from backend.app.stacks.identity_auth."
        "admin_read_dependencies import ("
        in source
    )

    assert (
        "AdministrativePrincipal,"
        in source
    )

    assert (
        "require_administrative_principal,"
        in source
    )

    expected_signature = (
        "async def get_administrative_user_statistics(\n"
        "    principal: AdministrativePrincipal = Depends(\n"
        "        require_administrative_principal\n"
        "    ),\n"
        "):"
    )

    assert expected_signature in source


def test_admin_statistics_no_longer_uses_custom_role_helper() -> None:
    source = BACKEND.read_text(
        encoding="utf-8",
    )

    assert (
        "def _require_admin_statistics_principal"
        not in source
    )

    assert (
        "_require_admin_statistics_principal("
        not in source
    )


def test_admin_statistics_dependency_reads_canonical_database_role() -> None:
    dependency = Path(
        "backend/app/stacks/identity_auth/"
        "admin_read_dependencies.py"
    ).read_text(
        encoding="utf-8",
    )

    assert (
        "IdentityUser.id == subject"
        in dependency
    )

    assert (
        "is_administrative_role("
        in dependency
    )

    assert (
        "canonical_role_value("
        in dependency
    )

    assert (
        "return AdministrativePrincipal("
        in dependency
    )

