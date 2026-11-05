from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

PROXY = (
    ROOT
    / "frontend/proxy.ts"
)

PREVIEW = (
    ROOT
    / "frontend/app/admin/user-dashboard/page.tsx"
)

LOGIN_ROUTE = (
    ROOT
    / "frontend/app/api/auth/login/route.ts"
)


def read(
    path: Path,
) -> str:
    assert path.exists(), (
        f"Missing required file: {path}"
    )

    return path.read_text(
        encoding="utf-8",
        errors="ignore",
    )


def test_admin_preview_links_to_real_user_dashboard() -> None:
    text = read(
        PREVIEW
    )

    assert (
        text.count(
            'href="/user/dashboard"'
        )
        >= 1
    )

    assert (
        "genuine lower-level User dashboard"
        in text
    )

    assert (
        "Impersonation"
        in text
    )

    assert (
        "Disabled"
        in text
    )


def test_administrative_identity_is_not_redirected_from_user_workspace() -> None:
    text = read(
        PROXY
    )

    forbidden = (
        '''isUserWorkspace &&
      administrative''',
        "isUserWorkspace && administrative",
    )

    for marker in forbidden:
        assert marker not in text


def test_regular_users_still_cannot_access_admin_workspace() -> None:
    text = read(
        PROXY
    )

    assert "isAdmin &&" in text
    assert "!administrative" in text
    assert "roleHomeRedirect(" in text


def test_non_developers_still_cannot_access_developer_dashboard() -> None:
    text = read(
        PROXY
    )

    assert (
        "isDeveloperDashboard &&"
        in text
    )

    assert "!developer" in text


def test_role_home_destinations_remain_canonical() -> None:
    proxy = read(
        PROXY
    )

    login = read(
        LOGIN_ROUTE
    )

    for marker in (
        'role === "developer"',
        'role === "owner"',
        '"/dashboard"',
        '"/admin"',
        '"/user/dashboard"',
    ):
        assert marker in proxy or marker in login


def test_downward_access_does_not_create_impersonation_parameter() -> None:
    combined = (
        read(PROXY)
        + "\n"
        + read(PREVIEW)
    ).lower()

    forbidden = (
        "impersonate=",
        "as_user=",
        "assume_user=",
        "user_override=",
        "role_override=",
    )

    for marker in forbidden:
        assert marker not in combined
