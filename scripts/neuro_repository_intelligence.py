#!/usr/bin/env python3
"""NeuroVest repository structural inventory v1.

Read-only source analysis. No source execution or AI calls.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import stat
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runtime/qualification/repository_intelligence_v1"

MAX_FILES = 30000
MAX_FILE_BYTES = 1024 * 1024
MAX_TOTAL_BYTES = 100 * 1024 * 1024

SOURCE_SUFFIXES = {
    ".py", ".ts", ".tsx", ".js", ".jsx",
    ".sql", ".sh", ".css", ".html",
}

SAFE_ROOTS = {
    "backend",
    "frontend",
    "alembic",
    "scripts",
    "tests",
}

EXCLUDE_DIRS = {
    ".git", ".venv", "venv", "node_modules",
    "__pycache__", ".next", ".pytest_cache",
    ".mypy_cache", ".ruff_cache",
    "runtime", "data", "uploads",
    "secrets", "private", "credentials",
    "backups", "logs", "dist", "build",
    "coverage", ".cache", "storage",
    "certs", "keys", "downloads",
    "vendor", ".tox", ".turbo",
}

EXCLUDE_NAMES = {
    ".env", ".env.local", ".env.production",
    "id_rsa", "id_ed25519",
    "credentials.json", "secrets.json",
    "service-account.json",
}

EXCLUDE_PATTERNS = (
    re.compile(r"(^|[._-])(secret|credential|password|token|private[-_]key)([._-]|$)", re.I),
    re.compile(r"\.(pem|key|p12|pfx|sqlite|db|log|bak|zip|tar|gz)$", re.I),
    re.compile(r"^\.env(?:\.|$)", re.I),
)

PY_ROUTE = re.compile(
    r"@(?:router|app|api_router)\."
    r"(get|post|put|patch|delete|websocket)\s*\("
)

JS_IMPORT = re.compile(
    r"""(?:from\s*['"]([^'"]+)['"]|"""
    r"""import\s*['"]([^'"]+)['"]|"""
    r"""require\s*\(\s*['"]([^'"]+)['"]\s*\))"""
)

records = []
dependencies = []
routes = []
errors = []
statistics = Counter()
total_bytes = 0

def blocked(name):
    return (
        name in EXCLUDE_NAMES
        or any(p.search(name) for p in EXCLUDE_PATTERNS)
    )

def analyze(path, relative):
    global total_bytes

    metadata = path.stat(follow_symlinks=False)

    if not stat.S_ISREG(metadata.st_mode):
        return

    if blocked(path.name):
        statistics["excluded_sensitive_names"] += 1
        return

    if path.suffix.lower() not in SOURCE_SUFFIXES:
        return

    if metadata.st_size > MAX_FILE_BYTES:
        statistics["oversized_files"] += 1
        return

    if total_bytes + metadata.st_size > MAX_TOTAL_BYTES:
        raise RuntimeError("MAX_TOTAL_ANALYSIS_BYTES_EXCEEDED")

    if len(records) >= MAX_FILES:
        raise RuntimeError("MAX_SOURCE_FILES_EXCEEDED")

    content = path.read_bytes()
    total_bytes += len(content)

    record = {
        "path": relative,
        "bytes": len(content),
        "sha256": hashlib.sha256(content).hexdigest(),
        "language": path.suffix.lower(),
    }

    statistics["source_files"] += 1
    statistics["bytes_examined"] += len(content)

    text = content.decode("utf-8", errors="replace")

    if path.suffix == ".py":
        try:
            tree = ast.parse(text, filename=relative)

            functions = 0
            classes = 0

            for node in ast.walk(tree):
                if isinstance(
                    node, (ast.FunctionDef, ast.AsyncFunctionDef)
                ):
                    functions += 1

                elif isinstance(node, ast.ClassDef):
                    classes += 1

                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        dependencies.append({
                            "source": relative,
                            "import": alias.name,
                        })

                elif isinstance(node, ast.ImportFrom):
                    dependencies.append({
                        "source": relative,
                        "import": "." * node.level
                        + (node.module or ""),
                    })

            record["functions"] = functions
            record["classes"] = classes

            for match in PY_ROUTE.finditer(text):
                routes.append({
                    "file": relative,
                    "method": match.group(1).upper(),
                    "line": text.count(
                        "\n", 0, match.start()
                    ) + 1,
                })

        except SyntaxError:
            statistics["python_syntax_errors"] += 1
            errors.append({
                "path": relative,
                "error": "PythonSyntaxError",
            })

    elif path.suffix.lower() in {
        ".js", ".jsx", ".ts", ".tsx"
    }:
        for match in JS_IMPORT.finditer(text):
            dependency = next(
                (group for group in match.groups() if group),
                None,
            )
            if dependency:
                dependencies.append({
                    "source": relative,
                    "import": dependency[:240],
                })

    records.append(record)

def main():
    global total_bytes

    print("=" * 72)
    print("NEUROVEST — REPOSITORY INTELLIGENCE V1")
    print("=" * 72)

    root_real = ROOT.resolve()

    for root_name in sorted(SAFE_ROOTS):
        start = ROOT / root_name

        if not start.is_dir() or start.is_symlink():
            continue

        for directory, dirs, files in os.walk(
            start, topdown=True, followlinks=False
        ):
            current = Path(directory)

            dirs[:] = sorted(
                name for name in dirs
                if not name.startswith(".next")
                and name not in EXCLUDE_DIRS
                and not blocked(name)
                and not (current / name).is_symlink()
            )

            for name in sorted(files):
                path = current / name

                if path.is_symlink():
                    statistics["symlinks_skipped"] += 1
                    continue

                relative = path.relative_to(ROOT).as_posix()

                try:
                    if not path.resolve().is_relative_to(root_real):
                        statistics["outside_root_skipped"] += 1
                        continue

                    analyze(path, relative)

                except (OSError, UnicodeError):
                    errors.append({
                        "path": relative,
                        "error": "FileReadError",
                    })

    by_language = Counter(
        record["language"] for record in records
    )

    by_area = Counter(
        record["path"].split("/")[0] for record in records
    )

    stack_counts = Counter()

    for record in records:
        parts = record["path"].split("/")
        if (
            len(parts) >= 5
            and parts[:3] == ["backend", "app", "stacks"]
        ):
            stack_counts[parts[3]] += 1

    result = {
        "schema": "neurovest.repository_intelligence.v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": sorted(SAFE_ROOTS),
        "limitations": [
            "Structural inventory, not full semantic understanding",
            "Secrets and runtime directories excluded",
            "No source code executed",
            "No repository content sent to an LLM",
            "Imports and routes are static approximations",
        ],
        "statistics": dict(statistics),
        "by_language": dict(sorted(by_language.items())),
        "by_area": dict(sorted(by_area.items())),
        "backend_stacks": dict(sorted(stack_counts.items())),
        "files": records,
        "imports": dependencies,
        "route_declarations": routes,
        "errors": errors[:250],
    }

    OUT.mkdir(parents=True, exist_ok=True)
    OUT.chmod(0o700)

    destination = OUT / "inventory.json"
    temp = OUT / ".inventory.pending"

    temp.write_text(
        json.dumps(result, indent=2) + "\n",
        encoding="utf-8",
    )
    temp.chmod(0o600)
    temp.replace(destination)

    print("INVENTORY_CREATED=PASS")
    print("SOURCE_FILES=", len(records))
    print("IMPORT_REFERENCES=", len(dependencies))
    print("ROUTE_DECLARATIONS=", len(routes))
    print("BYTES_EXAMINED=", total_bytes)
    print("PYTHON_SYNTAX_ERRORS=",
          statistics["python_syntax_errors"])
    print("ANALYSIS_ERRORS=", len(errors))

    print()
    print("=== MAJOR PROJECT AREAS ===")
    for area, count in sorted(by_area.items()):
        print(f"{area}={count}")

    print()
    print("=== BACKEND STACKS ===")
    for stack, count in sorted(stack_counts.items()):
        print(f"{stack}={count}")

    print()
    print("=== SOURCE LANGUAGES ===")
    for language, count in sorted(by_language.items()):
        print(f"{language}={count}")

    print()
    print("INVENTORY_FILE=", destination)
    print("REPOSITORY_INTELLIGENCE_V1=PASS")
    print("SOURCE_MODIFIED=False")
    print("PATCH_APPLIED=False")
    print("BACKEND_RESTARTED=False")
    print("DATABASE_MODIFIED=False")
    print("Terminal remains open.")

if __name__ == "__main__":
    main()
