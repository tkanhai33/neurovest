"""Portfolio inventory exact decimal storage.

Revision ID: portfolio_decimal_20260816
Revises: objective4gd_display_name
"""

from alembic import op
import sqlalchemy as sa


revision = "portfolio_decimal_20260816"
down_revision = "objective4gd_display_name"
branch_labels = None
depends_on = None


def upgrade():

    numeric_type = sa.Numeric(
        precision=46,
        scale=28,
    )

    for column_name in (
        "shares_quantity",
        "average_entry_price",
        "total_cost_basis",
        "realized_pnl",
    ):

        op.alter_column(
            "portfolio_inventory",
            column_name,
            existing_type=sa.Float(),
            type_=numeric_type,
            existing_nullable=False,
            postgresql_using=(
                f"{column_name}::numeric(46,28)"
            ),
        )


def downgrade():

    for column_name in (
        "shares_quantity",
        "average_entry_price",
        "total_cost_basis",
        "realized_pnl",
    ):

        op.alter_column(
            "portfolio_inventory",
            column_name,
            existing_type=sa.Numeric(
                precision=46,
                scale=28,
            ),
            type_=sa.Float(),
            existing_nullable=False,
            postgresql_using=(
                f"{column_name}::double precision"
            ),
        )
