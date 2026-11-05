from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "frontend"
BACKEND = ROOT / "backend/app"

IGNORED_PARTS = {
    ".next",
    "node_modules",
    "__pycache__",
    "runtime",
    "archive",
    "build",
    "dist",
}


def source_files(root: Path, suffixes: set[str]) -> list[Path]:
    return [
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix.lower() in suffixes
        and not any(part in IGNORED_PARTS for part in path.parts)
    ]


def combined(paths: list[Path]) -> str:
    return "\n".join(
        path.read_text(
            encoding="utf-8",
            errors="ignore",
        )
        for path in paths
    )


def test_frontend_contains_chat_api_request() -> None:
    text = combined(
        source_files(
            FRONTEND,
            {".ts", ".tsx", ".js", ".jsx"},
        )
    )

    assert re.search(
        r'["\'`]/api/[^"\'`]*chat[^"\'`]*["\'`]',
        text,
        re.IGNORECASE,
    )


def test_frontend_proxy_or_request_references_backend_chat_contract() -> None:
    text = combined(
        source_files(
            FRONTEND,
            {".ts", ".tsx", ".js", ".jsx"},
        )
    )

    assert (
        "/api/v1/chat" in text
        or re.search(
            r'fetch\s*\(\s*["\'`]/api/[^"\'`]*chat',
            text,
            re.IGNORECASE,
        )
    )


def test_backend_exposes_chat_route_contract() -> None:
    text = combined(
        source_files(
            BACKEND,
            {".py"},
        )
    )

    assert (
        "/api/v1/chat" in text
        or (
            re.search(
                r'prefix\s*=\s*["\']/api/v1',
                text,
                re.IGNORECASE,
            )
            and re.search(
                r'@router\.post\s*\(\s*["\']/chat',
                text,
                re.IGNORECASE,
            )
        )
    )
