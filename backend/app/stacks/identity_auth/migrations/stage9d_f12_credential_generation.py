"""
F12 credential-generation schema migration.

The generation table uses its own metadata registry.
Copy it into IdentityUser.metadata to resolve its user FK.
"""

from sqlalchemy import inspect

from backend.app.stacks.identity_auth.models import IdentityUser
from backend.app.stacks.identity_auth import credential_generation


TABLE_NAME = "identity_credential_generations"


def canonical_table():
    identity_metadata = IdentityUser.metadata
    source = credential_generation.metadata.tables.get(TABLE_NAME)

    if source is None:
        raise RuntimeError("Canonical generation table is missing")

    if "identity_users" not in identity_metadata.tables:
        raise RuntimeError("Canonical identity table is missing")

    table = identity_metadata.tables.get(TABLE_NAME)

    if table is None:
        table = source.to_metadata(identity_metadata)

    if not any(
        fk.target_fullname == "identity_users.id"
        for fk in table.foreign_keys
    ):
        raise RuntimeError("Unexpected generation foreign key")

    if not {"user_id", "generation"}.issubset(table.columns.keys()):
        raise RuntimeError("Unexpected generation column contract")

    return table


def upgrade(connection):
    table = canonical_table()
    table.create(bind=connection, checkfirst=True)

    inspector = inspect(connection)

    if not inspector.has_table(TABLE_NAME):
        raise RuntimeError("Generation table was not created")

    return True


def downgrade(connection):
    raise RuntimeError(
        "Destructive credential-generation downgrade is disabled"
    )
