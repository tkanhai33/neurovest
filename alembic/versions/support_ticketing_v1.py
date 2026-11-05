"""Create durable support ticketing tables.

Revision ID: support_ticketing_v1
Revises: news_intelligence_v1
Create Date: 2026-08-28
"""

from alembic import op
import sqlalchemy as sa


revision = "support_ticketing_v1"
down_revision = "news_intelligence_v1"
branch_labels = None
depends_on = None


def upgrade() -> None:

    op.create_table(
        "support_tickets",

        sa.Column(
            "id",
            sa.String(
                length=36
            ),
            nullable=False,
        ),

        sa.Column(
            "owner_user_id",
            sa.String(
                length=36
            ),
            nullable=False,
        ),

        sa.Column(
            "subject",
            sa.String(
                length=255
            ),
            nullable=False,
        ),

        sa.Column(
            "status",
            sa.String(
                length=32
            ),
            nullable=False,
            server_default="OPEN",
        ),

        sa.Column(
            "priority",
            sa.String(
                length=32
            ),
            nullable=False,
            server_default="NORMAL",
        ),

        sa.Column(
            "created_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=False,
            server_default=sa.func.now(),
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=False,
            server_default=sa.func.now(),
        ),

        sa.Column(
            "resolved_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=True,
        ),

        sa.Column(
            "closed_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=True,
        ),

        sa.CheckConstraint(
            "status IN ("
            "'OPEN', "
            "'WAITING_FOR_USER', "
            "'WAITING_FOR_ADMINISTRATOR', "
            "'RESOLVED', "
            "'CLOSED'"
            ")",
            name=(
                "ck_support_tickets_status"
            ),
        ),

        sa.CheckConstraint(
            "priority IN ("
            "'LOW', "
            "'NORMAL', "
            "'HIGH', "
            "'URGENT'"
            ")",
            name=(
                "ck_support_tickets_priority"
            ),
        ),

        sa.ForeignKeyConstraint(
            [
                "owner_user_id",
            ],
            [
                "identity_users.id",
            ],
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint(
            "id"
        ),
    )

    op.create_index(
        "ix_support_tickets_owner_user_id",
        "support_tickets",
        [
            "owner_user_id",
        ],
        unique=False,
    )

    op.create_index(
        "ix_support_tickets_status",
        "support_tickets",
        [
            "status",
        ],
        unique=False,
    )

    op.create_index(
        "ix_support_tickets_updated_at",
        "support_tickets",
        [
            "updated_at",
        ],
        unique=False,
    )


    op.create_table(
        "support_ticket_messages",

        sa.Column(
            "id",
            sa.String(
                length=36
            ),
            nullable=False,
        ),

        sa.Column(
            "ticket_id",
            sa.String(
                length=36
            ),
            nullable=False,
        ),

        sa.Column(
            "author_user_id",
            sa.String(
                length=36
            ),
            nullable=False,
        ),

        sa.Column(
            "author_role",
            sa.String(
                length=32
            ),
            nullable=False,
        ),

        sa.Column(
            "message",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=False,
            server_default=sa.func.now(),
        ),

        sa.CheckConstraint(
            "author_role IN ("
            "'USER', "
            "'ADMINISTRATOR'"
            ")",
            name=(
                "ck_support_ticket_messages_author_role"
            ),
        ),

        sa.ForeignKeyConstraint(
            [
                "ticket_id",
            ],
            [
                "support_tickets.id",
            ],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            [
                "author_user_id",
            ],
            [
                "identity_users.id",
            ],
            ondelete="RESTRICT",
        ),

        sa.PrimaryKeyConstraint(
            "id"
        ),
    )

    op.create_index(
        "ix_support_ticket_messages_ticket_id",
        "support_ticket_messages",
        [
            "ticket_id",
        ],
        unique=False,
    )

    op.create_index(
        "ix_support_ticket_messages_created_at",
        "support_ticket_messages",
        [
            "created_at",
        ],
        unique=False,
    )


def downgrade() -> None:

    op.drop_index(
        "ix_support_ticket_messages_created_at",
        table_name=(
            "support_ticket_messages"
        ),
    )

    op.drop_index(
        "ix_support_ticket_messages_ticket_id",
        table_name=(
            "support_ticket_messages"
        ),
    )

    op.drop_table(
        "support_ticket_messages"
    )

    op.drop_index(
        "ix_support_tickets_updated_at",
        table_name=(
            "support_tickets"
        ),
    )

    op.drop_index(
        "ix_support_tickets_status",
        table_name=(
            "support_tickets"
        ),
    )

    op.drop_index(
        "ix_support_tickets_owner_user_id",
        table_name=(
            "support_tickets"
        ),
    )

    op.drop_table(
        "support_tickets"
    )
