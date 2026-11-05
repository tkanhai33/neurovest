from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]

LOGIN_PAGE = ROOT / "frontend/app/login/page.tsx"
LOGIN_ROUTE = ROOT / "frontend/app/api/auth/login/route.ts"
E2E_FLOW = ROOT / "frontend/tests/e2e/05-authenticated-user-flow.spec.ts"


def read(path: Path) -> str:
    assert path.exists(), f"Missing required source file: {path}"
    return path.read_text(
        encoding="utf-8",
        errors="ignore",
    )


def test_successful_login_posts_to_frontend_auth_route() -> None:
    text = read(LOGIN_PAGE)

    assert '"/api/auth/login"' in text


def test_login_page_has_dashboard_default_destination() -> None:
    text = read(LOGIN_PAGE)

    assert re.search(
        r'["\']/dashboard["\']',
        text,
    )


def test_successful_login_navigates_to_resolved_destination() -> None:
    text = read(LOGIN_PAGE)

    assert re.search(
        r"router\.replace\s*\(\s*destination\s*\)",
        text,
    )


def test_frontend_login_route_returns_dashboard_redirect() -> None:
    text = read(LOGIN_ROUTE)

    assert re.search(
        r'return\s+["\']/dashboard["\']',
        text,
    )


def test_authenticated_e2e_flow_accepts_dashboard_destination() -> None:
    text = read(E2E_FLOW)

    assert '"/dashboard"' in text
    assert '"/user/dashboard"' in text
