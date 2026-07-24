from __future__ import annotations

from sqlalchemy import inspect

from backend.app.stacks.identity_auth.models import (
    IdentityRefreshSession,
    IdentityUser,
)

from backend.app.stacks.identity_auth.normalization import (
    normalize_email,
)

from backend.app.stacks.identity_auth.refresh_token_hashing import (
    hash_refresh_token,
    verify_refresh_token_hash,
)


def test_identity_user_schema_contract() -> None:
    columns = {
        column.name
        for column in inspect(
            IdentityUser
        ).columns
    }

    assert {
        "id",
        "email_normalized",
        "password_hash",
        "status",
        "is_active",
        "created_at",
        "updated_at",
    } <= columns


def test_refresh_session_schema_contract() -> None:
    columns = {
        column.name
        for column in inspect(
            IdentityRefreshSession
        ).columns
    }

    assert {
        "id",
        "user_id",
        "token_id",
        "token_hash",
        "family_id",
        "issued_at",
        "expires_at",
        "revoked_at",
        "replaced_by",
        "last_used_at",
        "created_at",
    } <= columns


def test_email_normalization_is_canonical() -> None:
    assert normalize_email(
        "  Travis@Example.COM "
    ) == "travis@example.com"


def test_refresh_token_hash_never_contains_raw_token() -> None:
    token = (
        "opaque-refresh-token-value"
    )

    pepper = b"x" * 32

    digest = hash_refresh_token(
        token,
        pepper=pepper,
    )

    assert token not in digest

    assert verify_refresh_token_hash(
        token,
        digest,
        pepper=pepper,
    ) is True

    assert verify_refresh_token_hash(
        "wrong-token",
        digest,
        pepper=pepper,
    ) is False
