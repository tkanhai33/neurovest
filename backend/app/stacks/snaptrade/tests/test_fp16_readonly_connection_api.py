from __future__ import annotations

import ast
from pathlib import Path

from fastapi.routing import APIRoute

from backend.app.main import app
from backend.app.stacks.snaptrade.api_router import (
    router,
)
from backend.app.stacks.identity_auth.api_dependencies import (
    require_authenticated_principal,
)


ROOT = Path(__file__).resolve().parents[5]

SERVICE = (
    ROOT
    / "backend/app/stacks/snaptrade/application/"
    "connection_service.py"
)

ROUTER = (
    ROOT
    / "backend/app/stacks/snaptrade/api_router.py"
)

MAIN = (
    ROOT
    / "backend/app/main.py"
)


def read(
    path: Path,
) -> str:
    assert path.exists(), (
        f"Missing required file: {path}"
    )

    return path.read_text(
        encoding="utf-8",
        errors="ignore",
    )


def snaptrade_routes() -> dict[
    str,
    APIRoute,
]:
    return {
        route.path: route
        for route in router.routes
        if isinstance(
            route,
            APIRoute,
        )
    }


def test_readonly_snaptrade_routes_are_decorated() -> None:
    routes = snaptrade_routes()

    assert set(
        routes
    ) == {
        "/api/v1/snaptrade/status",
        "/api/v1/snaptrade/register",
        "/api/v1/snaptrade/connection-portal",
        "/api/v1/snaptrade/synchronize",
        "/api/v1/snaptrade/balances",
        "/api/v1/snaptrade/portfolio",
        "/api/v1/snaptrade/portfolio/history",
    }

    assert routes[
        "/api/v1/snaptrade/status"
    ].methods == {
        "GET"
    }

    assert routes[
        "/api/v1/snaptrade/register"
    ].methods == {
        "POST"
    }

    assert routes[
        "/api/v1/snaptrade/connection-portal"
    ].methods == {
        "POST"
    }

    assert routes[
        "/api/v1/snaptrade/synchronize"
    ].methods == {
        "POST"
    }

    for path in (
        "/api/v1/snaptrade/balances",
        "/api/v1/snaptrade/portfolio",
        "/api/v1/snaptrade/portfolio/history",
    ):
        assert routes[path].methods == {
            "GET"
        }


def test_all_snaptrade_routes_require_authentication() -> None:
    for route in snaptrade_routes().values():
        dependency_calls = {
            dependency.call
            for dependency in (
                route.dependant.dependencies
            )
        }

        assert (
            require_authenticated_principal
            in dependency_calls
        )


def test_snaptrade_router_is_mounted_on_application() -> None:
    """
    FastAPI stores included routers lazily as _IncludedRouter objects.

    app.routes is therefore not guaranteed to expose every included
    APIRoute directly. The generated OpenAPI contract is the canonical
    flattened application route inventory.
    """

    schema = app.openapi()

    mounted = {
        path
        for path in schema.get(
            "paths",
            {}
        )
        if path.startswith(
            "/api/v1/snaptrade"
        )
    }

    expected = set(
        snaptrade_routes()
    )

    assert mounted == expected

    methods_by_path = {
        path: {
            method.upper()
            for method in operations
            if method.lower()
            in {
                "get",
                "post",
                "put",
                "patch",
                "delete",
            }
        }
        for path, operations in schema[
            "paths"
        ].items()
        if path in expected
    }

    assert methods_by_path == {
        "/api/v1/snaptrade/status": {
            "GET",
        },
        "/api/v1/snaptrade/register": {
            "POST",
        },
        "/api/v1/snaptrade/connection-portal": {
            "POST",
        },
        "/api/v1/snaptrade/synchronize": {
            "POST",
        },
        "/api/v1/snaptrade/balances": {
            "GET",
        },
        "/api/v1/snaptrade/portfolio": {
            "GET",
        },
        "/api/v1/snaptrade/portfolio/history": {
            "GET",
        },
    }


def test_connection_portal_is_read_only() -> None:
    text = read(
        SERVICE
    )

    assert (
        '"connection_type": "read"'
        in text
    )

    assert (
        '"trading_enabled": False'
        in text
    )


def test_service_does_not_reference_snaptrade_trading_namespace() -> None:
    text = read(
        SERVICE
    )

    forbidden = (
        ".trading.",
        ".trading",
        "place_order",
        "submit_order",
        "execute_order",
        "cancel_order",
        "replace_order",
        "trade-if-available",
        'connection_type": "trade"',
    )

    for marker in forbidden:
        assert marker not in text


def test_service_uses_only_approved_sdk_methods() -> None:
    text = read(
        SERVICE
    )

    assert (
        "register_snap_trade_user"
        in text
    )

    assert (
        "login_snap_trade_user"
        in text
    )

    assert (
        "list_user_accounts"
        in text
    )

    assert (
        "list_brokerage_authorizations"
        in text
    )


def test_service_uses_encrypted_owner_scoped_repository() -> None:
    text = read(
        SERVICE
    )

    assert (
        "SnapTradeCredentialRepository"
        in text
    )

    assert (
        "load_provider_identity"
        in text
    )

    assert (
        "store_registered_credential"
        in text
    )

    assert (
        "neurovest_user_id"
        in text
    )


def test_no_secret_is_returned_by_router_contract() -> None:
    text = read(
        ROUTER
    )

    tree = ast.parse(
        text
    )

    string_values = {
        node.value
        for node in ast.walk(
            tree
        )
        if isinstance(
            node,
            ast.Constant,
        )
        and isinstance(
            node.value,
            str,
        )
    }

    assert (
        "user_secret"
        not in string_values
    )

    assert (
        "userSecret"
        not in string_values
    )


def test_main_mounts_snaptrade_router() -> None:
    text = read(
        MAIN
    )

    assert (
        "router as snaptrade_router"
        in text
    )

    assert (
        "app.include_router(snaptrade_router)"
        in text
    )
