from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from fastapi.routing import APIRoute

from backend.app.stacks.identity_auth.admin_mutation_router import (
    router,
)
from backend.app.stacks.identity_auth.admin_mutation_service import (
    AdministrativeUserMutationService,
    _generate_temporary_password,
)


def test_admin_mutation_routes_are_exact() -> None:
    expected = {
        (
            "/api/v1/admin/users/"
            "{user_id}/require-password-reset"
        ): {"POST"},
        (
            "/api/v1/admin/users/"
            "{user_id}/temporary-password"
        ): {"POST"},
        (
            "/api/v1/admin/users/"
            "{user_id}/disable"
        ): {"POST"},
        (
            "/api/v1/admin/users/"
            "{user_id}/enable"
        ): {"POST"},
        "/api/v1/admin/users/{user_id}": {
            "DELETE",
        },
    }

    actual = {
        route.path: set(route.methods or set())
        for route in router.routes
        if isinstance(route, APIRoute)
    }

    assert actual == expected


def test_temporary_password_policy() -> None:
    password = _generate_temporary_password()

    assert len(password) >= 20
    assert any(c.islower() for c in password)
    assert any(c.isupper() for c in password)
    assert any(c.isdigit() for c in password)
    assert any(
        c in "!@#$%^&*"
        for c in password
    )


@pytest.mark.parametrize(
    "role",
    [
        "dev",
        "developer",
        "owner",
    ],
)
def test_protected_roles_denied(
    role: str,
) -> None:
    service = AdministrativeUserMutationService(
        session=SimpleNamespace()
    )

    target = SimpleNamespace(
        id="protected-user",
        role=role,
    )

    with pytest.raises(
        HTTPException
    ) as captured:
        service._assert_target_mutable(
            actor_id="administrator",
            target=target,
        )

    assert captured.value.status_code == 403


def test_self_mutation_denied() -> None:
    service = AdministrativeUserMutationService(
        session=SimpleNamespace()
    )

    target = SimpleNamespace(
        id="administrator",
        role="admin",
    )

    with pytest.raises(
        HTTPException
    ) as captured:
        service._assert_target_mutable(
            actor_id="administrator",
            target=target,
        )

    assert captured.value.status_code == 403
