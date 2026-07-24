#!/usr/bin/env python3

"""
Read-only filesystem helpers for Phase 135.

These helpers inspect repository paths but never modify application code.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable


DEFAULT_EXCLUDED_DIRECTORIES = {
    ".git",
    ".idea",
    ".mypy_cache",
    ".next",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "htmlcov",
    "node_modules",
    "runtime",
    "venv",
}


def is_excluded_path(
    path: Path,
    repository_root: Path,
    excluded_directories: set[str] | None = None,
) -> bool:
    """
    Return True when a path is contained inside an excluded directory.
    """

    excluded = excluded_directories or DEFAULT_EXCLUDED_DIRECTORIES

    try:
        relative = path.resolve().relative_to(repository_root.resolve())
    except ValueError:
        return True

    return any(part in excluded for part in relative.parts)


def iter_repository_files(
    repository_root: Path,
    excluded_directories: set[str] | None = None,
) -> Iterable[Path]:
    """
    Yield repository files in stable lexical order.
    """

    root = repository_root.resolve()

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue

        if is_excluded_path(
            path=path,
            repository_root=root,
            excluded_directories=excluded_directories,
        ):
            continue

        yield path


def safe_relative_path(path: Path, repository_root: Path) -> str:
    """
    Return a normalized repository-relative POSIX path.
    """

    try:
        return path.resolve().relative_to(repository_root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def safe_file_size(path: Path) -> int:
    """
    Return file size, or zero if the file cannot be inspected.
    """

    try:
        return path.stat().st_size
    except OSError:
        return 0


def safe_read_text(
    path: Path,
    max_bytes: int = 1_000_000,
) -> str | None:
    """
    Read a likely text file safely.

    Large files and binary files are skipped.
    """

    try:
        size = path.stat().st_size
    except OSError:
        return None

    if size > max_bytes:
        return None

    try:
        raw = path.read_bytes()
    except OSError:
        return None

    if b"\x00" in raw:
        return None

    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return raw.decode("utf-8", errors="replace")
        except Exception:
            return None
