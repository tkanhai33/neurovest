from __future__ import annotations

import inspect

from fastapi.routing import APIRoute

from backend.app.main import app
from backend.app.stacks.identity_auth.admin_read_api_models import (
    AdministrativeSessionDetail,
    AdministrativeSessionSummary,
    AdministrativeUserDetail,
    AdministrativeUserSummary,
)
from backend.app.stacks.identity_auth import (
    admin_read_dependencies,
    admin_read_models,
)


PROHIBITED_FIELDS = {
    "password",
    "password_hash",
    "hashed_password",
    "access_token",
    "refresh_token",
    "token_hash",
    "jwt",
    "secret",
}


def model_fields(
    model: type,
) -> set[str]:
    return set(
        model.model_fields
    )


def test_user_models_expose_no_secrets() -> None:
    for model in (
        AdministrativeUserSummary,
        AdministrativeUserDetail,
    ):
        fields = model_fields(
            model
        )

        assert not (
            fields
            & PROHIBITED_FIELDS
        )


def test_session_models_expose_no_secrets() -> None:
    for model in (
        AdministrativeSessionSummary,
        AdministrativeSessionDetail,
    ):
        fields = model_fields(
            model
        )

        assert not (
            fields
            & PROHIBITED_FIELDS
        )


def test_admin_routes_are_get_only() -> None:
    from backend.app.stacks.identity_auth.admin_read_router import (
        router as administrative_read_router,
    )

    expected = {
        "/api/v1/admin/introspection",
        "/api/v1/admin/users",
        "/api/v1/admin/users/{user_id}",
        "/api/v1/admin/sessions",
        "/api/v1/admin/sessions/{session_id}",
    }

    router_routes = {
        route.path: set(
            route.methods or set()
        )
        for route in administrative_read_router.routes
        if isinstance(
            route,
            APIRoute,
        )
    }

    # Stage 9D-C2 owns and freezes these five routes.
    # Later qualified stages may add additional administrative
    # read-only routes without invalidating the C2 contract.
    assert expected <= set(router_routes)

    for path in expected:
        assert router_routes[path] == {
            "GET",
        }

    schema = app.openapi()
    schema_paths = schema.get(
        "paths",
        {},
    )

    for path in expected:
        assert path in schema_paths

        methods = {
            method.lower()
            for method in schema_paths[path]
            if method.lower()
            in {
                "get",
                "post",
                "put",
                "patch",
                "delete",
                "options",
                "head",
                "trace",
            }
        }

        # Stage 9D-C2 owns and freezes the GET operation.
        # Later qualified stages may add separately authorized
        # operations to the same canonical resource path.
        assert "get" in methods

        if path != "/api/v1/admin/users/{user_id}":
            assert methods == {
                "get",
            }



def test_admin_dependency_is_database_authoritative() -> None:
    source = inspect.getsource(
        admin_read_dependencies
    )

    assert "IdentityUser.id == subject" in source
    assert "user.role" not in source
    assert 'getattr(\n            user,\n            "role"' in source
    assert "principal.claims" not in source
    assert "ADMINISTRATIVE_ROLES" in source
    assert "must_change_password" in source


def test_read_service_does_not_serialize_secret_fields() -> None:
    source = inspect.getsource(
        admin_read_models
    )

    prohibited_assignments = (
        "password_hash=",
        "token_hash=",
        "refresh_token=",
        "access_token=",
        "secret=",
    )

    for prohibited in prohibited_assignments:
        assert prohibited not in source


def test_openapi_contains_only_expected_admin_methods() -> None:
    schema = app.openapi()

    expected = {
        "/api/v1/admin/introspection",
        "/api/v1/admin/users",
        "/api/v1/admin/users/{user_id}",
        "/api/v1/admin/sessions",
        "/api/v1/admin/sessions/{session_id}",
    }

    for path in expected:
        assert path in schema["paths"]

        operations = {
            operation.lower()
            for operation in schema["paths"][path]
            if operation.lower()
            in {
                "get",
                "post",
                "put",
                "patch",
                "delete",
                "options",
                "head",
                "trace",
            }
        }

        # Stage 9D-C2 freezes the original GET operation.
        # The user-detail resource is shared with Stage 9D-C5-B,
        # which separately qualifies DELETE on the same path.
        assert "get" in operations

        if path == "/api/v1/admin/users/{user_id}":
            assert operations <= {
                "get",
                "delete",
            }
        else:
            assert operations == {
                "get",
            }


def test_no_password_reset_route_added_in_c2() -> None:
    from backend.app.stacks.identity_auth.admin_read_router import (
        router as administrative_read_router,
    )

    read_router_paths = {
        route.path
        for route in administrative_read_router.routes
        if isinstance(
            route,
            APIRoute,
        )
    }

    # Stage 9D-C2 owns only the administrative read router.
    # Its router must remain free of password-reset mutations.
    assert not any(
        "reset" in route_path
        for route_path in read_router_paths
    )

    schema = app.openapi()
    schema_paths = schema.get(
        "paths",
        {},
    )

    authorized_reset_path = (
        "/api/v1/admin/users/"
        "{user_id}/require-password-reset"
    )

    if authorized_reset_path in schema_paths:
        operations = {
            operation.lower()
            for operation in schema_paths[
                authorized_reset_path
            ]
            if operation.lower()
            in {
                "get",
                "post",
                "put",
                "patch",
                "delete",
                "options",
                "head",
                "trace",
            }
        }

        assert operations == {
            "post",
        }
