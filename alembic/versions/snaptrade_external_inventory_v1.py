"""Create owner-scoped SnapTrade external portfolio inventory.

Revision ID: snaptrade_external_inventory_v1
Revises: objective4gd_display_name
Create Date: 2026-08-16
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "snaptrade_external_inventory_v1"

down_revision = "objective4gd_display_name"

branch_labels = None

depends_on = None


def upgrade() -> None:

    op.create_table(
        "snaptrade_external_portfolio_positions",

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
            "position_id_hash",
            sa.String(
                length=64
            ),
            nullable=False,
        ),

        sa.Column(
            "symbol",
            sa.String(
                length=64
            ),
            nullable=False,
        ),

        sa.Column(
            "instrument_kind",
            sa.String(
                length=64
            ),
            nullable=True,
        ),

        sa.Column(
            "currency",
            sa.String(
                length=16
            ),
            nullable=True,
        ),

        sa.Column(
            "shares_quantity",
            sa.Numeric(
                precision=38,
                scale=18,
            ),
            nullable=False,
        ),

        sa.Column(
            "average_entry_price",
            sa.Numeric(
                precision=38,
                scale=18,
            ),
            nullable=True,
        ),

        sa.Column(
            "current_price",
            sa.Numeric(
                precision=38,
                scale=18,
            ),
            nullable=True,
        ),

        sa.Column(
            "market_value",
            sa.Numeric(
                precision=38,
                scale=18,
            ),
            nullable=True,
        ),

        sa.Column(
            "total_cost_basis",
            sa.Numeric(
                precision=38,
                scale=18,
            ),
            nullable=True,
        ),

        sa.Column(
            "unrealized_gain",
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
            "id",
        ),

        sa.UniqueConstraint(
            "neurovest_user_id",
            "account_id_hash",
            "position_id_hash",
            name=(
                "uq_snaptrade_external_position_"
                "owner_account_position"
            ),
        ),
    )


    op.create_index(
        "ix_snaptrade_external_position_owner",
        "snaptrade_external_portfolio_positions",
        [
            "neurovest_user_id",
        ],
        unique=False,
    )


    op.create_index(
        "ix_snaptrade_external_position_owner_symbol",
        "snaptrade_external_portfolio_positions",
        [
            "neurovest_user_id",
            "symbol",
        ],
        unique=False,
    )


    op.create_index(
        "ix_snaptrade_external_position_account",
        "snaptrade_external_portfolio_positions",
        [
            "account_id_hash",
        ],
        unique=False,
    )


def downgrade() -> None:

    op.drop_index(
        "ix_snaptrade_external_position_account",
        table_name=(
            "snaptrade_external_portfolio_positions"
        ),
    )

    op.drop_index(
        "ix_snaptrade_external_position_owner_symbol",
        table_name=(
            "snaptrade_external_portfolio_positions"
        ),
    )

    op.drop_index(
        "ix_snaptrade_external_position_owner",
        table_name=(
            "snaptrade_external_portfolio_positions"
        ),
    )

    op.drop_table(
        "snaptrade_external_portfolio_positions"
    )
