from types import MappingProxyType, SimpleNamespace

import pytest
from fastapi import HTTPException

from backend.app.stacks.chat_public.developer_role_guard import (
    authenticated_developer_role,
)
from backend.app.stacks.chat_public.developer_code_api import (
    _require_developer,
)


def principal(role="developer", subject="developer-user"):
    return SimpleNamespace(
        subject=subject,
        claims=MappingProxyType({
            "authorization_role": role,
        }),
    )


def test_developer_claim_allowed():
    assert authenticated_developer_role(principal())


@pytest.mark.parametrize("role", [
    "user", "admin", "guest", None, "", "developer-admin",
])
def test_other_roles_denied(role):
    assert not authenticated_developer_role(principal(role))


def test_missing_principal_denied():
    assert not authenticated_developer_role(None)


def test_missing_subject_denied():
    assert not authenticated_developer_role(
        SimpleNamespace(subject="", claims={"role": "developer"})
    )


def test_role_claim_cannot_be_supplied_as_direct_attribute():
    assert not authenticated_developer_role(
        SimpleNamespace(
            subject="user-a",
            role="developer",
            claims={"authorization_role": "user"},
        )
    )


def test_api_accepts_developer_claim():
    _require_developer(principal())


def test_api_rejects_regular_user():
    with pytest.raises(HTTPException) as exc:
        _require_developer(principal("user"))
    assert exc.value.status_code == 403


def test_api_rejects_forged_direct_role():
    forged = SimpleNamespace(
        role="developer",
        subject="regular-user",
        claims={"sub": "regular-user", "role": "user"},
    )
    with pytest.raises(HTTPException):
        _require_developer(forged)
