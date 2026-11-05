from __future__ import annotations

import ast
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
LEDGER_ROOT = ROOT / "backend/app/stacks/journal_ledger"

IGNORED_PARTS = {
    "tests",
    "test",
    "migrations",
    "__pycache__",
}

DELETE_SQL = re.compile(
    r"\bDELETE\s+FROM\b",
    re.IGNORECASE,
)

UPDATE_SQL = re.compile(
    r"\bUPDATE\s+[A-Za-z_][A-Za-z0-9_]*\s+SET\b",
    re.IGNORECASE,
)

FORBIDDEN_CALLS = {
    "delete",
    "remove",
    "destroy",
    "truncate",
    "bulk_delete",
    "update",
    "bulk_update",
}


def production_files() -> list[Path]:
    return sorted(
        path
        for path in LEDGER_ROOT.rglob("*.py")
        if not any(
            part in IGNORED_PARTS
            for part in path.parts
        )
    )


def call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id

    if isinstance(node, ast.Attribute):
        return node.attr

    return None


def test_ledger_has_no_existing_record_mutation_calls() -> None:
    violations: list[str] = []

    for path in production_files():
        text = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        tree = ast.parse(
            text,
            filename=str(path),
        )

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue

            name = call_name(node.func)

            if name and name.lower() in FORBIDDEN_CALLS:
                violations.append(
                    f"{path.relative_to(ROOT)}:{node.lineno}: {name}"
                )

    assert violations == [], "\n".join(violations)


def test_ledger_has_no_delete_sql() -> None:
    violations: list[str] = []

    for path in production_files():
        text = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        if DELETE_SQL.search(text):
            violations.append(
                str(path.relative_to(ROOT))
            )

    assert violations == [], "\n".join(violations)


def test_ledger_has_no_update_sql() -> None:
    violations: list[str] = []

    for path in production_files():
        text = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        if UPDATE_SQL.search(text):
            violations.append(
                str(path.relative_to(ROOT))
            )

    assert violations == [], "\n".join(violations)
