from __future__ import annotations

import pytest

from backend.app.stacks.identity_auth.errors import (
    RevokedTokenError,
)

from backend.app.stacks.identity_auth.revocation import (
    InMemoryTokenRevocationStore,
)

from backend.app.stacks.identity_auth.tokens import (
    issue_refresh_token,
    rotate_refresh_token,
    validate_access_token,
    validate_refresh_token,
)


TEST_SECRET = (
    "test-only-secret-material-"
    "0123456789abcdef"
)


@pytest.fixture(autouse=True)
def jwt_secret(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "NEUROVEST_JWT_SECRET",
        TEST_SECRET,
    )


def test_refresh_rotation_revokes_previous_token() -> None:
    store = InMemoryTokenRevocationStore()

    original = issue_refresh_token(
        "user-1",
        extra_claims={
            "role": "viewer",
        },
        now=1000,
    )

    replacement = rotate_refresh_token(
        original,
        revocation_store=store,
        now=1001,
    )

    with pytest.raises(
        RevokedTokenError
    ):
        validate_refresh_token(
            original,
            revocation_store=store,
            now=1002,
        )

    new_refresh = validate_refresh_token(
        replacement.refresh_token,
        revocation_store=store,
        now=1002,
    )

    new_access = validate_access_token(
        replacement.access_token,
        revocation_store=store,
        now=1002,
    )

    assert new_refresh.subject == "user-1"
    assert new_access.subject == "user-1"
    assert new_access.extra[
        "role"
    ] == "viewer"


def test_refresh_token_cannot_be_rotated_twice() -> None:
    store = InMemoryTokenRevocationStore()

    original = issue_refresh_token(
        "user-1",
        now=1000,
    )

    rotate_refresh_token(
        original,
        revocation_store=store,
        now=1001,
    )

    with pytest.raises(
        RevokedTokenError
    ):
        rotate_refresh_token(
            original,
            revocation_store=store,
            now=1002,
        )
