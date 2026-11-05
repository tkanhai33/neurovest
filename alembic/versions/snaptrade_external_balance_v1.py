"""SnapTrade dedicated external balance inventory.

Revision ID: snaptrade_external_balance_v1
Revises: strategy_knowledge_name_v1
"""

from alembic import op
import sqlalchemy as sa


revision = "snaptrade_external_balance_v1"
down_revision = "strategy_knowledge_name_v1"
branch_labels = None
depends_on = None


def upgrade() -> None:

    op.create_table(
        "snaptrade_external_balances",

        sa.Column(
            "id",
            sa.String(
                length=36
            ),
            nullable=False,
        ),

        sa.Column(
            "neurovest_user_id",
            sa.String(
                length=36
            ),
            nullable=False,
        ),

        sa.Column(
            "account_id_hash",
            sa.String(
                length=64
            ),
            nullable=False,
        ),

        sa.Column(
            "currency",
            sa.String(
                length=16
            ),
            nullable=False,
        ),

        sa.Column(
            "cash_amount",
            sa.Numeric(
                precision=38,
                scale=18,
            ),
            nullable=True,
        ),

        sa.Column(
            "buying_power",
            sa.Numeric(
                precision=38,
                scale=18,
            ),
            nullable=True,
        ),

        sa.Column(
            "cash_available",
            sa.Numeric(
                precision=38,
                scale=18,
            ),
            nullable=True,
        ),

        sa.Column(
            "settled_cash",
            sa.Numeric(
                precision=38,
                scale=18,
            ),
            nullable=True,
        ),

        sa.Column(
            "source_provider",
            sa.String(
                length=32
            ),
            nullable=False,
        ),

        sa.Column(
            "read_only",
            sa.Boolean(),
            nullable=False,
        ),

        sa.Column(
            "last_synced_at",
            sa.DateTime(
                timezone=True
            ),
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
            "id"
        ),

        sa.UniqueConstraint(
            "neurovest_user_id",
            "account_id_hash",
            "currency",
            name=(
                "uq_snaptrade_external_balance_"
                "owner_account_currency"
            ),
        ),
    )


    op.create_index(
        "ix_snaptrade_external_balance_owner",
        "snaptrade_external_balances",
        [
            "neurovest_user_id",
        ],
        unique=False,
    )


    op.create_index(
        "ix_snaptrade_external_balance_account",
        "snaptrade_external_balances",
        [
            "account_id_hash",
        ],
        unique=False,
    )


    op.execute(
        """
        GRANT SELECT, INSERT, UPDATE, DELETE
        ON TABLE snaptrade_external_balances
        TO neurovest
        """
    )


def downgrade() -> None:

    op.execute(
        """
        REVOKE SELECT, INSERT, UPDATE, DELETE
        ON TABLE snaptrade_external_balances
        FROM neurovest
        """
    )

    op.drop_index(
        "ix_snaptrade_external_balance_account",
        table_name=(
            "snaptrade_external_balances"
        ),
    )

    op.drop_index(
        "ix_snaptrade_external_balance_owner",
        table_name=(
            "snaptrade_external_balances"
        ),
    )

    op.drop_table(
        "snaptrade_external_balances"
    )
