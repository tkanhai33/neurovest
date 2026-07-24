"""Create durable identity and refresh-session persistence.

Revision ID: iqc_s5_jwt_identity_sessions
Revises: ws3_stage5_decision_events
"""

from alembic import op
import sqlalchemy as sa


revision = "iqc_s5_jwt_identity_sessions"

down_revision = "ws3_stage5_decision_events"

branch_labels = None

depends_on = None


def upgrade() -> None:
    op.create_table(
        "identity_users",
        sa.Column(
            "id",
            sa.String(
                length=36
            ),
            nullable=False,
        ),
        sa.Column(
            "email_normalized",
            sa.String(
                length=320
            ),
            nullable=False,
        ),
        sa.Column(
            "password_hash",
            sa.String(
                length=512
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(
                length=32
            ),
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name="pk_identity_users",
        ),
        sa.UniqueConstraint(
            "email_normalized",
            name=(
                "uq_identity_users_"
                "email_normalized"
            ),
        ),
    )

    op.create_index(
        "ix_identity_users_status",
        "identity_users",
        [
            "status",
        ],
        unique=False,
    )

    op.create_table(
        "identity_refresh_sessions",
        sa.Column(
            "id",
            sa.String(
                length=36
            ),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.String(
                length=36
            ),
            nullable=False,
        ),
        sa.Column(
            "token_id",
            sa.String(
                length=64
            ),
            nullable=False,
        ),
        sa.Column(
            "token_hash",
            sa.String(
                length=64
            ),
            nullable=False,
        ),
        sa.Column(
            "family_id",
            sa.String(
                length=36
            ),
            nullable=False,
        ),
        sa.Column(
            "issued_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=False,
        ),
        sa.Column(
            "expires_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=False,
        ),
        sa.Column(
            "revoked_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=True,
        ),
        sa.Column(
            "replaced_by",
            sa.String(
                length=64
            ),
            nullable=True,
        ),
        sa.Column(
            "last_used_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            [
                "user_id",
            ],
            [
                "identity_users.id",
            ],
            name=(
                "fk_identity_refresh_sessions_"
                "user_id_identity_users"
            ),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=(
                "pk_identity_refresh_sessions"
            ),
        ),
        sa.UniqueConstraint(
            "token_id",
            name=(
                "uq_identity_refresh_sessions_"
                "token_id"
            ),
        ),
    )

    op.create_index(
        "ix_identity_refresh_sessions_family",
        "identity_refresh_sessions",
        [
            "family_id",
        ],
        unique=False,
    )

    op.create_index(
        "ix_identity_refresh_sessions_user_active",
        "identity_refresh_sessions",
        [
            "user_id",
            "revoked_at",
            "expires_at",
        ],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_identity_refresh_sessions_user_active",
        table_name="identity_refresh_sessions",
    )

    op.drop_index(
        "ix_identity_refresh_sessions_family",
        table_name="identity_refresh_sessions",
    )

    op.drop_table(
        "identity_refresh_sessions"
    )

    op.drop_index(
        "ix_identity_users_status",
        table_name="identity_users",
    )

    op.drop_table(
        "identity_users"
    )
