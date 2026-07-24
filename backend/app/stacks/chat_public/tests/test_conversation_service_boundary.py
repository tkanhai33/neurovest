from __future__ import annotations

import ast
from pathlib import Path

from backend.app.stacks.chat_public import conversation_service
from backend.app.stacks.chat_public import conversation_store


ROOT = Path(".").resolve()

CHAT_ROOT = (
    ROOT
    / "backend"
    / "app"
    / "stacks"
    / "chat_public"
)

SERVICE_FILE = (
    CHAT_ROOT
    / "conversation_service.py"
)


def _imports(path: Path) -> set[str]:
    tree = ast.parse(
        path.read_text(
            encoding="utf-8"
        ),
        filename=str(path),
    )

    modules = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name)

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                modules.add(node.module)

    return modules


def _owns_route(path: Path) -> bool:
    tree = ast.parse(
        path.read_text(
            encoding="utf-8"
        ),
        filename=str(path),
    )

    route_methods = {
        "get",
        "post",
        "put",
        "patch",
        "delete",
        "route",
        "websocket",
    }

    for node in ast.walk(tree):
        if not isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            continue

        for decorator in node.decorator_list:
            expression = (
                decorator.func
                if isinstance(
                    decorator,
                    ast.Call,
                )
                else decorator
            )

            if (
                isinstance(
                    expression,
                    ast.Attribute,
                )
                and expression.attr
                in route_methods
            ):
                return True

    return False


def test_service_exports_existing_store_symbols() -> None:
    assert conversation_service.__all__

    for name in conversation_service.__all__:
        assert hasattr(
            conversation_store,
            name,
        )

        assert getattr(
            conversation_service,
            name,
        ) is getattr(
            conversation_store,
            name,
        )


def test_service_has_no_direct_persistence_imports() -> None:
    imports = _imports(
        SERVICE_FILE
    )

    forbidden = {
        module
        for module in imports
        if (
            module.startswith("sqlalchemy")
            or "db_runtime" in module
            or "chat_models" in module
        )
    }

    assert forbidden == set()


def test_route_owners_do_not_import_store_or_persistence() -> None:
    violations = []

    for path in sorted(
        (
            ROOT
            / "backend"
            / "app"
        ).rglob("*.py")
    ):
        if "__pycache__" in path.parts:
            continue

        if not _owns_route(path):
            continue

        imports = _imports(path)

        chat_service_modules = {
            "backend.app.stacks.chat_public.conversation_service",
            "app.stacks.chat_public.conversation_service",
            "stacks.chat_public.conversation_service",
        }

        if not (
            imports
            & chat_service_modules
        ):
            continue

        forbidden = sorted(
            module
            for module in imports
            if (
                module.startswith("sqlalchemy")
                or "db_runtime" in module
                or "chat_models" in module
                or module.endswith(
                    "chat_public.conversation_store"
                )
            )
        )

        if forbidden:
            violations.append(
                {
                    "path": path.relative_to(
                        ROOT
                    ).as_posix(),
                    "imports": forbidden,
                }
            )

    assert violations == []


def test_external_production_consumers_do_not_import_store() -> None:
    violations = []

    store_modules = {
        "backend.app.stacks.chat_public.conversation_store",
        "app.stacks.chat_public.conversation_store",
        "stacks.chat_public.conversation_store",
    }

    for path in sorted(
        (
            ROOT
            / "backend"
            / "app"
        ).rglob("*.py")
    ):
        if "__pycache__" in path.parts:
            continue

        lowered_parts = {
            part.lower()
            for part in path.parts
        }

        if (
            "test" in lowered_parts
            or "tests" in lowered_parts
            or path.name.startswith("test_")
        ):
            continue

        if path in {
            SERVICE_FILE,
            CHAT_ROOT / "conversation_store.py",
        }:
            continue

        imports = _imports(path)

        matched = sorted(
            imports
            & store_modules
        )

        if matched:
            violations.append(
                {
                    "path": path.relative_to(
                        ROOT
                    ).as_posix(),
                    "imports": matched,
                }
            )

    assert violations == []
