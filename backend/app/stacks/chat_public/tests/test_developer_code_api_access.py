import pytest
from fastapi import HTTPException
from types import SimpleNamespace

from backend.app.stacks.chat_public.developer_code_api import (
    _require_developer,
    CodeProposalRequest,
)


@pytest.mark.parametrize("role", [
    "user", "admin", "guest", "", None, "developer-admin",
])
def test_rejects_non_developer_roles(role):
    with pytest.raises(HTTPException) as raised:
        _require_developer(SimpleNamespace(role=role))
    assert raised.value.status_code == 403


def test_allows_explicit_developer_role():
    from backend.app.stacks.identity_auth.contracts import (
        AuthenticatedPrincipal,
    )

    principal = AuthenticatedPrincipal(
        subject="developer-user",
        token_id="test-token",
        claims={"authorization_role": "developer"},
    )

    _require_developer(principal)


def test_request_defaults_to_bounded_source():
    request = CodeProposalRequest(
        task="Improve the repository inspection ranking."
    )
    assert request.source_file.endswith(
        "developer_repository_inspection.py"
    )
