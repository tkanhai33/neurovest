from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]

CHAT_ROUTE = (
    ROOT
    / "frontend"
    / "app"
    / "api"
    / "v1"
    / "chat"
    / "route.ts"
)

PROXY = (
    ROOT
    / "frontend"
    / "proxy.ts"
)


def read(path: Path) -> str:
    assert path.is_file(), f"Required source is missing: {path}"
    return path.read_text(encoding="utf-8")


def test_chat_route_forwards_browser_csrf_header() -> None:
    source = read(CHAT_ROUTE)

    assert (
        'request.headers.get("x-csrf-token")'
        in source
    )

    assert (
        'request.headers.get("x-csrftoken")'
        in source
    )

    assert (
        '"X-CSRF-Token"'
        in source
    )

    assert (
        "headers: backendHeaders"
        in source
    )

    assert (
        'backendFetch(\n      "/api/v1/chat"'
        in source
    )

    assert (
        '"X-Neurovest-Source": "frontend_chat"'
        in source
    )


def test_chat_proxy_allows_exact_internal_route() -> None:
    source = read(PROXY)

    constants = re.findall(
        r'const\s+INTERNAL_CHAT_API_PATH\s*=\s*'
        r'["\']/api/v1/chat["\'];',
        source,
    )

    comparisons = re.findall(
        r'request\.nextUrl\.pathname\s*===\s*'
        r'INTERNAL_CHAT_API_PATH',
        source,
        flags=re.DOTALL,
    )

    assert len(constants) == 1
    assert len(comparisons) == 1

    comparison = re.search(
        r'''
        if\s*\(
        \s*request\.nextUrl\.pathname
        \s*===\s*
        INTERNAL_CHAT_API_PATH
        \s*\)\s*\{
        \s*return\s+NextResponse\.next\(\);
        \s*\}
        ''',
        source,
        flags=re.DOTALL | re.VERBOSE,
    )

    assert comparison is not None


def test_chat_bypass_is_exact_not_prefix_based() -> None:
    source = read(PROXY)

    assert (
        "request.nextUrl.pathname ==="
        in source
    )

    assert not re.search(
        r'request\.nextUrl\.pathname\.startsWith\(\s*'
        r'INTERNAL_CHAT_API_PATH',
        source,
    )

    assert not re.search(
        r'INTERNAL_CHAT_API_PATH\.startsWith\(',
        source,
    )


def test_existing_api_matcher_remains_enabled() -> None:
    source = read(PROXY)

    assert (
        '"/api/v1/:path*"'
        in source
    )


def test_security_chain_remains_in_chat_route() -> None:
    source = read(CHAT_ROUTE)

    assert (
        'import { backendFetch }'
        in source
    )

    assert (
        'method: "POST"'
        in source
    )

    assert (
        '"Content-Type": "application/json"'
        in source
    )

    assert (
        "body: JSON.stringify(payload)"
        in source
    )
