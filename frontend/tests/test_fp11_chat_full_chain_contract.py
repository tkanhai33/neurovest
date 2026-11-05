from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]

CHAT_SERVICE = ROOT / "frontend/services/chatService.ts"
NEXT_ROUTE = ROOT / "frontend/app/api/v1/chat/route.ts"
BACKEND_AUTH = ROOT / "frontend/lib/backendAuth.ts"
BACKEND_ROUTE = ROOT / "backend/app/stacks/chat_public/chat_api.py"


def read(path: Path) -> str:
    assert path.exists(), f"Missing required source file: {path}"

    return path.read_text(
        encoding="utf-8",
        errors="ignore",
    )


def test_chat_service_calls_frontend_chat_endpoint() -> None:
    text = read(CHAT_SERVICE)

    assert re.search(
        r'CHAT_ENDPOINT\s*=\s*["\']/api/v1/chat["\']',
        text,
    )

    assert re.search(
        r'fetch\s*\(\s*CHAT_ENDPOINT',
        text,
        re.DOTALL,
    )


def test_next_chat_route_uses_authenticated_backend_helper() -> None:
    text = read(NEXT_ROUTE)

    assert re.search(
        r'import\s*\{\s*backendFetch\s*\}',
        text,
    )

    assert re.search(
        r'backendFetch\s*\(\s*["\']/api/v1/chat["\']',
        text,
        re.DOTALL,
    )

    assert re.search(
        r'method\s*:\s*["\']POST["\']',
        text,
    )


def test_backend_fetch_calls_configured_backend() -> None:
    text = read(BACKEND_AUTH)

    assert "BACKEND_BASE_URL" in text

    assert re.search(
        r'fetch\s*\(\s*`\$\{BACKEND_BASE_URL\}\$\{normalizedPath\}`',
        text,
        re.DOTALL,
    )

    assert re.search(
        r'Authorization',
        text,
    )


def test_backend_exposes_matching_post_route() -> None:
    text = read(BACKEND_ROUTE)

    assert re.search(
        r'@router\.post\s*\(\s*["\']/api/v1/chat["\']',
        text,
        re.DOTALL,
    )
