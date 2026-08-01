from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

ROUTE = (
    ROOT
    / "frontend"
    / "app"
    / "api"
    / "auth"
    / "refresh"
    / "route.ts"
)


def source() -> str:
    return ROUTE.read_text(
        encoding="utf-8"
    )


def test_refresh_proxy_exists() -> None:
    assert ROUTE.is_file()


def test_refresh_proxy_exports_post() -> None:
    assert (
        "export async function POST"
        in source()
    )


def test_refresh_proxy_reads_refresh_cookie() -> None:
    text = source()

    assert (
        '"neurovest_refresh"'
        in text
    )

    assert (
        "refreshToken"
        in text
    )


def test_refresh_proxy_sends_required_body_field() -> None:
    text = source()

    assert (
        "JSON.stringify({"
        in text
    )

    assert (
        "refresh_token:"
        in text
    )

    assert (
        "refreshToken"
        in text
    )


def test_refresh_proxy_calls_backend_endpoint() -> None:
    text = source()

    assert (
        "/auth/refresh"
        in text
    )

    assert (
        "BACKEND_BASE_URL"
        in text
    )


def test_refresh_proxy_forwards_csrf() -> None:
    text = source()

    assert (
        "x-csrf-token"
        in text.lower()
    )

    assert (
        "X-CSRF-Token"
        in text
    )

    assert (
        "neurovest_csrf"
        in text
    )


def test_refresh_proxy_preserves_backend_cookies() -> None:
    text = source()

    assert (
        "getSetCookie"
        in text
    )

    assert (
        "Set-Cookie"
        in text
    )

    assert (
        "appendBackendCookies"
        in text
    )


def test_refresh_proxy_installs_returned_tokens() -> None:
    text = source()

    assert (
        "installReturnedTokens"
        in text
    )

    assert (
        '"neurovest_access"'
        in text
    )

    assert (
        '"neurovest_refresh"'
        in text
    )

    assert (
        '"neurovest_csrf"'
        in text
    )

    assert (
        '"neurovest_session"'
        in text
    )


def test_refresh_proxy_rejects_missing_refresh_token() -> None:
    text = source()

    assert (
        "Refresh token is missing"
        in text
    )

    assert (
        "401"
        in text
    )


def test_refresh_proxy_disables_caching() -> None:
    assert (
        '"no-store"'
        in source()
    )


def test_refresh_proxy_fails_closed() -> None:
    text = source()

    assert (
        "Authentication service unavailable"
        in text
    )

    assert (
        "503"
        in text
    )
