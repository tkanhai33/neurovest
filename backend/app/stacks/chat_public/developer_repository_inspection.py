"""Bounded, read-only source inspection for authenticated developer chat."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CODE_ROOT = ROOT / "backend" / "app"

STOP_WORDS = frozenset({
    "the", "and", "for", "with", "from", "into", "that", "this",
    "what", "where", "which", "does", "have", "your", "neuro",
    "neurovest", "code", "file", "files", "system", "about",
    "please", "show", "find", "explain", "inspect", "improve",
    "developer", "function", "functions", "change", "modify",
    "could", "would", "should", "want", "need", "make", "using",
})

SENSITIVE_NAMES = (
    ".env", "credential", "secret", "private_key",
    "token_store", "password_dump",
)

def _is_sensitive_term(stripped: str) -> bool:
    return any(term in stripped.lower() for term in (
        "password=", "secret=", "api_key=", "token=",
        "authorization:", "bearer ",
    ))


def inspect_repository(query: str, *, max_files: int = 5) -> str:
    """Return bounded references to existing application Python source.

    This function has no write or command-execution capabilities.
    """
    if not isinstance(query, str):
        return ""

    words = [
        word.lower()
        for word in re.findall(r"[A-Za-z_][A-Za-z_0-9]{2,}", query)
        if word.lower() not in STOP_WORDS
    ]
    words = list(dict.fromkeys(words))[:12]

    if not words:
        return ""

    if not CODE_ROOT.is_dir():
        return "Repository inspection unavailable: source directory missing."

    results = []

    for path in CODE_ROOT.rglob("*.py"):
        if any(part.startswith(".") or part == "__pycache__"
               for part in path.relative_to(CODE_ROOT).parts):
            continue

        if any(marker in path.name.lower() for marker in SENSITIVE_NAMES):
            continue

        if path.is_symlink():
            continue

        try:
            if path.stat().st_size > 180_000:
                continue
            relative = path.relative_to(ROOT).as_posix()
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError):
            continue

        path_matches = sum(word in relative.lower() for word in words)
        matches = []

        for number, line in enumerate(lines, 1):
            stripped = line.strip()

            # Avoid exposing likely inline credentials or tokens.
            if _is_sensitive_term(stripped):
                continue

            matched = sum(word in stripped.lower() for word in words)
            if matched:
                matches.append((matched, number, stripped[:150]))

        score = path_matches * 5 + sum(
            matched for matched, _, _ in matches[:15]
        )

        if score:
            matches.sort(key=lambda x: (-x[0], x[1]))
            results.append((score, relative, matches[:3]))

    results.sort(key=lambda x: (-x[0], x[1]))

    if not results:
        return "No matching Python source was found in backend/app."

    output = ["### Repository source matches"]

    for _, relative, matches in results[:max_files]:
        output.append(f"**`{relative}`**")
        for _, number, snippet in matches:
            output.append(f"- Line {number}: `{snippet}`")

    output.append(
        "These are read-only source matches, not proof of a defect "
        "or evidence that any modification or test was performed."
    )

    return "\n".join(output)
