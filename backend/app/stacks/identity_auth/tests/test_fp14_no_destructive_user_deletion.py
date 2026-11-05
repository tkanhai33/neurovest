from __future__ import annotations

import ast
from pathlib import Path

from fastapi.routing import APIRoute

from backend.app.stacks.identity_auth.admin_mutation_router import (
    router,
)


ROOT = Path(__file__).resolve().parents[5]

ROUTER = (
    ROOT
    / "backend/app/stacks/identity_auth/admin_mutation_router.py"
)

SERVICE = (
    ROOT
    / "backend/app/stacks/identity_auth/admin_mutation_service.py"
)

MODELS = (
    ROOT
    / "backend/app/stacks/identity_auth/admin_mutation_api_models.py"
)


def read(path: Path) -> str:
    assert path.exists(), (
        f"Missing required source file: {path}"
    )

    return path.read_text(
        encoding="utf-8",
        errors="ignore",
    )


def function_names(
    path: Path,
) -> set[str]:
    tree = ast.parse(
        read(path),
        filename=str(path),
    )

    return {
        node.name
        for node in ast.walk(tree)
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
    }


def test_admin_user_router_has_no_delete_method() -> None:
    violations = []

    for route in router.routes:
        if not isinstance(
            route,
            APIRoute,
        ):
            continue

        methods = set(
            route.methods
            or set()
        )

        if "DELETE" in methods:
            violations.append(
                f"{route.path}: {sorted(methods)}"
            )

    assert violations == [], "\n".join(
        violations
    )


def test_admin_user_router_retains_disable_and_enable_routes() -> None:
    routes = {
        route.path: set(
            route.methods
            or set()
        )
        for route in router.routes
        if isinstance(
            route,
            APIRoute,
        )
    }

    assert (
        routes[
            "/api/v1/admin/users/{user_id}/disable"
        ]
        == {"POST"}
    )

    assert (
        routes[
            "/api/v1/admin/users/{user_id}/enable"
        ]
        == {"POST"}
    )


def test_destructive_delete_account_function_is_absent() -> None:
    assert (
        "delete_account"
        not in function_names(
            ROUTER
        )
    )

    assert (
        "delete_account"
        not in function_names(
            SERVICE
        )
    )


def test_admin_mutation_service_never_deletes_identity_target() -> None:
    text = read(
        SERVICE
    )

    forbidden = (
        "self._session.delete(",
        "await self._session.delete(",
        'action="delete_account"',
        "AdministrativeDeleteResponse",
        "deleted=True",
    )

    violations = [
        marker
        for marker in forbidden
        if marker in text
    ]

    assert violations == []


def test_disable_account_is_non_destructive_and_revokes_sessions() -> None:
    text = read(
        SERVICE
    )

    start = text.index(
        "async def disable_account"
    )

    end = text.index(
        "async def enable_account",
        start,
    )

    block = text[
        start:
        end
    ]

    assert "target.is_active = False" in block
    assert '_set_status(target, "disabled")' in block
    assert "_revoke_refresh_sessions" in block
    assert "await self._session.commit()" in block
    assert "self._session.delete" not in block


def test_delete_response_contract_is_absent() -> None:
    text = read(
        MODELS
    )

    assert (
        "AdministrativeDeleteResponse"
        not in text
    )

    assert "deleted: bool" not in text
