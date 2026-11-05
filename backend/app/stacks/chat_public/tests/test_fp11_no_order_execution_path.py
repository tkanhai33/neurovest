from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]

PRODUCTION_ROOTS = [
    ROOT / "backend/app/stacks/chat_public",
    ROOT / "backend/app/llm_bridge",
]

FORBIDDEN_MODULE_SEGMENTS = (
    ".stacks.execution",
    ".stacks.paper_trading",
    ".stacks.broker_integration",
    ".stacks.snaptrade",
)

FORBIDDEN_CALLS = {
    "process_portfolio_output",
    "execute_order",
    "execute_trade",
    "submit_order",
    "place_order",
    "create_order",
    "send_order",
    "submit_authenticated_paper_order",
}

FORBIDDEN_ORDER_ROUTES = {
    "/api/v1/paper/orders",
}


def production_python_files() -> list[Path]:
    files: list[Path] = []

    for root in PRODUCTION_ROOTS:
        if not root.exists():
            continue

        for path in root.rglob("*.py"):
            if "tests" in path.parts:
                continue

            if "__pycache__" in path.parts:
                continue

            files.append(path)

    return sorted(files)


def dotted_call_name(node: ast.Call) -> str | None:
    if isinstance(node.func, ast.Name):
        return node.func.id

    if not isinstance(node.func, ast.Attribute):
        return None

    parts: list[str] = []
    current = node.func

    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value

    if isinstance(current, ast.Name):
        parts.append(current.id)

    return ".".join(reversed(parts))


def test_chat_production_code_has_no_execution_imports() -> None:
    violations: list[str] = []

    for path in production_python_files():
        text = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        tree = ast.parse(
            text,
            filename=str(path),
        )

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""

                if any(
                    segment in module
                    for segment in FORBIDDEN_MODULE_SEGMENTS
                ):
                    violations.append(
                        f"{path.relative_to(ROOT)}:{node.lineno}: "
                        f"from {module} import ..."
                    )

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if any(
                        segment in alias.name
                        for segment in FORBIDDEN_MODULE_SEGMENTS
                    ):
                        violations.append(
                            f"{path.relative_to(ROOT)}:{node.lineno}: "
                            f"import {alias.name}"
                        )

    assert violations == [], "\n".join(violations)


def test_chat_production_code_has_no_order_execution_calls() -> None:
    violations: list[str] = []

    for path in production_python_files():
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

            name = dotted_call_name(node)

            if not name:
                continue

            final_name = name.split(".")[-1]

            if final_name in FORBIDDEN_CALLS:
                violations.append(
                    f"{path.relative_to(ROOT)}:{node.lineno}: {name}"
                )

    assert violations == [], "\n".join(violations)


def test_chat_production_code_has_no_order_submission_route() -> None:
    violations: list[str] = []

    for path in production_python_files():
        text = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        for route in FORBIDDEN_ORDER_ROUTES:
            if route in text:
                violations.append(
                    f"{path.relative_to(ROOT)}: references {route}"
                )

    assert violations == [], "\n".join(violations)
