from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

ROUTE = (
    ROOT
    / "frontend"
    / "app"
    / "api"
    / "auth"
    / "logout"
    / "route.ts"
)


def source() -> str:
    return ROUTE.read_text(
        encoding="utf-8"
    )


def test_logout_proxy_exists() -> None:
    assert ROUTE.is_file()


def test_logout_proxy_exports_post() -> None:
    assert (
        "export async function POST"
        in source()
    )


def test_logout_proxy_reads_refresh_cookie() -> None:
    text = source()

    assert '"neurovest_refresh"' in text
    assert "refreshToken" in text


def test_logout_proxy_sends_refresh_token_body() -> None:
    text = source()

    assert "JSON.stringify({" in text
    assert "refresh_token:" in text
    assert "refreshToken" in text


def test_logout_proxy_calls_backend_logout() -> None:
    text = source()

    assert "/auth/logout" in text
    assert "BACKEND_BASE_URL" in text


def test_logout_proxy_forwards_csrf() -> None:
    text = source()

    assert "x-csrf-token" in text.lower()
    assert "X-CSRF-Token" in text
    assert "neurovest_csrf" in text


def test_logout_proxy_clears_auth_cookies() -> None:
    text = source()

    for cookie in (
        "neurovest_access",
        "neurovest_refresh",
        "neurovest_csrf",
        "neurovest_session",
    ):
        assert cookie in text

    assert "clearAuthenticationCookies" in text
    assert "maxAge:" in text
    assert "new Date(0)" in text


def test_logout_proxy_preserves_backend_cookies() -> None:
    text = source()

    assert "getSetCookie" in text
    assert "Set-Cookie" in text
    assert "appendBackendCookies" in text


def test_logout_proxy_disables_caching() -> None:
    assert '"no-store"' in source()


def test_logout_proxy_fails_closed() -> None:
    text = source()

    assert (
        "Authentication service unavailable"
        in text
    )

    assert "503" in text
