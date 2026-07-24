"""Add optional display name to identity users.

Revision ID: objective4gd_display_name
Revises: objective3e_owner_schema
Create Date: 2026-07-22
"""

from alembic import op
import sqlalchemy as sa


revision = "objective4gd_display_name"
down_revision = "objective3e_owner_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "identity_users",
        sa.Column(
            "display_name",
            sa.String(length=100),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "identity_users",
        "display_name",
    )
