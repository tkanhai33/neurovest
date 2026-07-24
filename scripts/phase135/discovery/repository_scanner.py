#!/usr/bin/env python3

"""
Blind repository discovery scanner.

The scanner makes no architecture assumptions. It inventories what actually
exists in the repository and reports observable structure only.
"""

from __future__ import annotations

import hashlib
import os
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from scripts.phase135.utils.filesystem import (
    iter_repository_files,
    safe_file_size,
    safe_read_text,
    safe_relative_path,
)


SOURCE_EXTENSIONS = {
    ".c",
    ".cc",
    ".cpp",
    ".css",
    ".go",
    ".h",
    ".hpp",
    ".html",
    ".java",
    ".js",
    ".jsx",
    ".mjs",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".scss",
    ".sh",
    ".sql",
    ".svelte",
    ".ts",
    ".tsx",
    ".vue",
}

CONFIG_FILENAMES = {
    ".dockerignore",
    ".editorconfig",
    ".env",
    ".env.example",
    ".eslintrc",
    ".eslintrc.json",
    ".gitignore",
    ".pre-commit-config.yaml",
    "alembic.ini",
    "compose.yaml",
    "compose.yml",
    "docker-compose.yaml",
    "docker-compose.yml",
    "dockerfile",
    "eslint.config.js",
    "eslint.config.mjs",
    "jest.config.js",
    "jest.config.ts",
    "makefile",
    "next.config.js",
    "next.config.mjs",
    "next.config.ts",
    "package-lock.json",
    "package.json",
    "pnpm-lock.yaml",
    "pyproject.toml",
    "pytest.ini",
    "requirements-dev.txt",
    "requirements.txt",
    "ruff.toml",
    "setup.cfg",
    "setup.py",
    "tailwind.config.js",
    "tailwind.config.ts",
    "tsconfig.json",
    "vite.config.js",
    "vite.config.ts",
    "yarn.lock",
}

TEST_NAME_MARKERS = (
    "test_",
    "_test.",
    ".test.",
    ".spec.",
)

ENTRYPOINT_FILENAMES = {
    "__main__.py",
    "app.py",
    "main.py",
    "manage.py",
    "server.py",
    "wsgi.py",
    "asgi.py",
    "index.js",
    "index.ts",
    "index.tsx",
    "page.tsx",
    "route.ts",
}


@dataclass(frozen=True)
class FileRecord:
    path: str
    name: str
    suffix: str
    size_bytes: int
    category: str
    is_source: bool
    is_test: bool
    is_config: bool
    is_entrypoint_candidate: bool
    sha256: str | None


class RepositoryScanner:
    """
    Perform a deterministic, read-only repository inventory.
    """

    def __init__(self, repository_root: Path) -> None:
        self.repository_root = repository_root.resolve()

    def scan(self) -> dict[str, Any]:
        files: list[FileRecord] = []

        directory_file_counts: Counter[str] = Counter()
        extension_counts: Counter[str] = Counter()
        category_counts: Counter[str] = Counter()
        top_level_counts: Counter[str] = Counter()
        duplicate_hashes: dict[str, list[str]] = defaultdict(list)

        total_bytes = 0
        text_files = 0
        binary_or_unreadable_files = 0

        for path in iter_repository_files(self.repository_root):
            relative_path = safe_relative_path(path, self.repository_root)
            size_bytes = safe_file_size(path)
            suffix = path.suffix.lower()
            name_lower = path.name.lower()

            category = self._categorize_file(path)
            is_source = suffix in SOURCE_EXTENSIONS
            is_test = self._is_test_file(path)
            is_config = self._is_config_file(path)
            is_entrypoint_candidate = self._is_entrypoint_candidate(path)

            file_hash = self._hash_file(path, size_bytes)

            if file_hash:
                duplicate_hashes[file_hash].append(relative_path)

            content = safe_read_text(path, max_bytes=250_000)

            if content is None:
                binary_or_unreadable_files += 1
            else:
                text_files += 1

            directory = str(Path(relative_path).parent.as_posix())
            top_level = Path(relative_path).parts[0] if Path(relative_path).parts else "."

            directory_file_counts[directory] += 1
            extension_counts[suffix or "<none>"] += 1
            category_counts[category] += 1
            top_level_counts[top_level] += 1
            total_bytes += size_bytes

            files.append(
                FileRecord(
                    path=relative_path,
                    name=path.name,
                    suffix=suffix,
                    size_bytes=size_bytes,
                    category=category,
                    is_source=is_source,
                    is_test=is_test,
                    is_config=is_config,
                    is_entrypoint_candidate=is_entrypoint_candidate,
                    sha256=file_hash,
                )
            )

        directories = self._discover_directories()
        duplicate_groups = self._build_duplicate_groups(duplicate_hashes)

        source_files = [record for record in files if record.is_source]
        test_files = [record for record in files if record.is_test]
        config_files = [record for record in files if record.is_config]
        entrypoint_candidates = [
            record for record in files if record.is_entrypoint_candidate
        ]

        return {
            "repository_root": str(self.repository_root),
            "repository_name": self.repository_root.name,
            "summary": {
                "total_files": len(files),
                "total_directories": len(directories),
                "total_bytes": total_bytes,
                "source_files": len(source_files),
                "test_files": len(test_files),
                "config_files": len(config_files),
                "entrypoint_candidates": len(entrypoint_candidates),
                "text_files": text_files,
                "binary_or_unreadable_files": binary_or_unreadable_files,
                "duplicate_file_groups": len(duplicate_groups),
            },
            "top_level_entries": self._discover_top_level_entries(),
            "top_level_file_counts": dict(sorted(top_level_counts.items())),
            "extension_counts": dict(
                sorted(
                    extension_counts.items(),
                    key=lambda item: (-item[1], item[0]),
                )
            ),
            "category_counts": dict(
                sorted(
                    category_counts.items(),
                    key=lambda item: (-item[1], item[0]),
                )
            ),
            "directory_file_counts": dict(
                sorted(
                    directory_file_counts.items(),
                    key=lambda item: (-item[1], item[0]),
                )
            ),
            "directories": directories,
            "files": [asdict(record) for record in files],
            "source_files": [record.path for record in source_files],
            "test_files": [record.path for record in test_files],
            "config_files": [record.path for record in config_files],
            "entrypoint_candidates": [
                record.path for record in entrypoint_candidates
            ],
            "duplicate_file_groups": duplicate_groups,
        }

    def _discover_directories(self) -> list[str]:
        directories: list[str] = []

        for current_root, directory_names, _ in os.walk(self.repository_root):
            current_path = Path(current_root)

            directory_names[:] = sorted(
                name
                for name in directory_names
                if name
                not in {
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
            )

            if current_path == self.repository_root:
                continue

            directories.append(
                safe_relative_path(current_path, self.repository_root)
            )

        return sorted(directories)

    def _discover_top_level_entries(self) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = []

        try:
            children = sorted(
                self.repository_root.iterdir(),
                key=lambda path: path.name.lower(),
            )
        except OSError:
            return entries

        excluded = {
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

        for child in children:
            if child.name in excluded:
                continue

            entries.append(
                {
                    "name": child.name,
                    "type": (
                        "directory"
                        if child.is_dir()
                        else "file"
                        if child.is_file()
                        else "other"
                    ),
                    "size_bytes": safe_file_size(child) if child.is_file() else None,
                }
            )

        return entries

    @staticmethod
    def _categorize_file(path: Path) -> str:
        suffix = path.suffix.lower()
        name = path.name.lower()

        if suffix in SOURCE_EXTENSIONS:
            return "source"

        if name in CONFIG_FILENAMES:
            return "configuration"

        if suffix in {".md", ".rst", ".txt"}:
            return "documentation"

        if suffix in {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg"}:
            return "structured_data_or_configuration"

        if suffix in {".csv", ".parquet", ".feather", ".xlsx"}:
            return "data"

        if suffix in {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico"}:
            return "image"

        if suffix in {".pdf", ".doc", ".docx", ".ppt", ".pptx"}:
            return "document"

        if suffix in {".lock"} or name.endswith(".lock"):
            return "dependency_lock"

        return "other"

    @staticmethod
    def _is_test_file(path: Path) -> bool:
        normalized = path.as_posix().lower()
        name = path.name.lower()

        return (
            any(marker in name for marker in TEST_NAME_MARKERS)
            or "/tests/" in f"/{normalized}/"
            or "/test/" in f"/{normalized}/"
            or name == "conftest.py"
        )

    @staticmethod
    def _is_config_file(path: Path) -> bool:
        name = path.name.lower()

        return (
            name in CONFIG_FILENAMES
            or name.startswith(".env")
            or path.suffix.lower() in {".toml", ".yaml", ".yml", ".ini", ".cfg"}
        )

    @staticmethod
    def _is_entrypoint_candidate(path: Path) -> bool:
        name = path.name.lower()

        if name in ENTRYPOINT_FILENAMES:
            return True

        if path.suffix.lower() == ".sh":
            return True

        return False

    @staticmethod
    def _hash_file(path: Path, size_bytes: int) -> str | None:
        if size_bytes <= 0 or size_bytes > 5_000_000:
            return None

        digest = hashlib.sha256()

        try:
            with path.open("rb") as file_handle:
                for chunk in iter(lambda: file_handle.read(65_536), b""):
                    digest.update(chunk)
        except OSError:
            return None

        return digest.hexdigest()

    @staticmethod
    def _build_duplicate_groups(
        duplicate_hashes: dict[str, list[str]],
    ) -> list[dict[str, Any]]:
        groups: list[dict[str, Any]] = []

        for file_hash, paths in sorted(duplicate_hashes.items()):
            unique_paths = sorted(set(paths))

            if len(unique_paths) < 2:
                continue

            groups.append(
                {
                    "sha256": file_hash,
                    "file_count": len(unique_paths),
                    "paths": unique_paths,
                }
            )

        return groups
