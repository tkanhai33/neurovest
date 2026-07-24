from __future__ import annotations

import ast
from pathlib import Path

import pytest

from backend.app.stacks.identity_auth.models import (
    IdentityUser,
)

from backend.app.stacks.identity_auth.repositories import (
    APPROVED_IDENTITY_ROLES,
    normalize_identity_role,
)


def test_identity_model_declares_stage9d_a_fields() -> None:
    columns = IdentityUser.__table__.columns

    assert "role" in columns
    assert "must_change_password" in columns

    assert columns["role"].nullable is False
    assert (
        columns[
            "must_change_password"
        ].nullable
        is False
    )


def test_identity_role_contract_is_canonical() -> None:
    assert APPROVED_IDENTITY_ROLES == {
        "user",
        "admin",
        "owner",
    }

    assert normalize_identity_role(
        " OWNER "
    ) == "owner"


@pytest.mark.parametrize(
    "invalid",
    (
        "",
        "administrator",
        "system_admin",
        "root",
        "superuser",
    ),
)
def test_identity_role_contract_rejects_unknown_roles(
    invalid: str,
) -> None:
    with pytest.raises(
        ValueError
    ):
        normalize_identity_role(
            invalid
        )


def test_identity_model_has_role_check_constraint() -> None:
    names = {
        constraint.name
        for constraint
        in IdentityUser.__table__.constraints
    }

    assert (
        "ck_identity_users_role"
        in names
    )


def test_stage9d_a_migration_is_versioned_and_idempotent() -> None:
    path = Path(
        "backend/app/stacks/identity_auth/"
        "migrations/"
        "stage9d_a_identity_schema.py"
    )

    source = path.read_text(
        encoding="utf-8"
    )

    ast.parse(
        source,
        filename=str(path),
    )

    assert "MIGRATION_ID" in source
    assert "async def upgrade" in source
    assert "async def downgrade" in source
    assert "ADD COLUMN IF NOT EXISTS role" in source
    assert "must_change_password" in source
    assert "CREATE INDEX IF NOT EXISTS" in source
    assert "ck_identity_users_role" in source
