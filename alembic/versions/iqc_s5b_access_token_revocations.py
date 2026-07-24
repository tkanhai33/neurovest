"""Add durable access-token revocation records.

Revision ID: iqc_s5b_access_token_revocations
Revises: iqc_s5_jwt_identity_sessions
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "iqc_s5b_access_token_revocations"
down_revision = "iqc_s5_jwt_identity_sessions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "identity_access_token_revocations",
        sa.Column(
            "id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "token_id",
            sa.String(length=64),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "issued_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "expires_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "revoked_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "reason",
            sa.String(length=64),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=(
                "pk_identity_access_token_"
                "revocations"
            ),
        ),
        sa.UniqueConstraint(
            "token_id",
            name=(
                "uq_identity_access_token_"
                "revocations_token_id"
            ),
        ),
    )

    op.create_index(
        "ix_identity_access_token_"
        "revocations_user_id",
        "identity_access_token_revocations",
        [
            "user_id",
        ],
        unique=False,
    )

    op.create_index(
        "ix_identity_access_token_"
        "revocations_expires_at",
        "identity_access_token_revocations",
        [
            "expires_at",
        ],
        unique=False,
    )

    op.create_index(
        "ix_identity_access_token_"
        "revocations_revoked_at",
        "identity_access_token_revocations",
        [
            "revoked_at",
        ],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_identity_access_token_"
        "revocations_revoked_at",
        table_name=(
            "identity_access_token_revocations"
        ),
    )

    op.drop_index(
        "ix_identity_access_token_"
        "revocations_expires_at",
        table_name=(
            "identity_access_token_revocations"
        ),
    )

    op.drop_index(
        "ix_identity_access_token_"
        "revocations_user_id",
        table_name=(
            "identity_access_token_revocations"
        ),
    )

    op.drop_table(
        "identity_access_token_revocations"
    )
