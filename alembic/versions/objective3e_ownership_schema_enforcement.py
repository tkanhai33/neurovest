"""Enforce portfolio ownership schema.

Revision ID: objective3e_owner_schema
Revises: objective2_portfolio_owner
Create Date: 2026-07-20
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "objective3e_owner_schema"
down_revision: str | None = "objective2_portfolio_owner"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


OLD_SYMBOL_CONSTRAINT = (
    "portfolio_inventory_symbol_key"
)

OWNER_SYMBOL_CONSTRAINT = (
    "uq_portfolio_inventory_user_id_symbol"
)


def _assert_upgrade_data_is_safe() -> None:
    connection = op.get_bind()

    invalid_orders = connection.execute(
        sa.text(
            """
            SELECT count(*)
            FROM order_history
            WHERE user_id IS NULL
               OR btrim(user_id) = ''
            """
        )
    ).scalar_one()

    invalid_positions = connection.execute(
        sa.text(
            """
            SELECT count(*)
            FROM portfolio_inventory
            WHERE user_id IS NULL
               OR btrim(user_id) = ''
            """
        )
    ).scalar_one()

    duplicate_pairs = connection.execute(
        sa.text(
            """
            SELECT count(*)
            FROM (
                SELECT
                    user_id,
                    symbol
                FROM portfolio_inventory
                GROUP BY
                    user_id,
                    symbol
                HAVING count(*) > 1
            ) duplicate_rows
            """
        )
    ).scalar_one()

    if invalid_orders:
        raise RuntimeError(
            "Objective 3E blocked: order_history "
            "contains invalid owners"
        )

    if invalid_positions:
        raise RuntimeError(
            "Objective 3E blocked: portfolio_inventory "
            "contains invalid owners"
        )

    if duplicate_pairs:
        raise RuntimeError(
            "Objective 3E blocked: duplicate "
            "(user_id, symbol) rows exist"
        )


def _assert_downgrade_data_is_safe() -> None:
    connection = op.get_bind()

    shared_symbols = connection.execute(
        sa.text(
            """
            SELECT count(*)
            FROM (
                SELECT
                    symbol
                FROM portfolio_inventory
                GROUP BY symbol
                HAVING count(*) > 1
            ) shared_symbol_rows
            """
        )
    ).scalar_one()

    if shared_symbols:
        raise RuntimeError(
            "Objective 3E downgrade blocked: "
            "multiple owners currently hold the same symbol"
        )


def upgrade() -> None:
    _assert_upgrade_data_is_safe()

    op.alter_column(
        "order_history",
        "user_id",
        existing_type=sa.String(length=36),
        nullable=False,
    )

    op.alter_column(
        "portfolio_inventory",
        "user_id",
        existing_type=sa.String(length=36),
        nullable=False,
    )

    op.drop_constraint(
        OLD_SYMBOL_CONSTRAINT,
        "portfolio_inventory",
        type_="unique",
    )

    op.create_unique_constraint(
        OWNER_SYMBOL_CONSTRAINT,
        "portfolio_inventory",
        [
            "user_id",
            "symbol",
        ],
    )


def downgrade() -> None:
    _assert_downgrade_data_is_safe()

    op.drop_constraint(
        OWNER_SYMBOL_CONSTRAINT,
        "portfolio_inventory",
        type_="unique",
    )

    op.create_unique_constraint(
        OLD_SYMBOL_CONSTRAINT,
        "portfolio_inventory",
        [
            "symbol",
        ],
    )

    op.alter_column(
        "portfolio_inventory",
        "user_id",
        existing_type=sa.String(length=36),
        nullable=True,
    )

    op.alter_column(
        "order_history",
        "user_id",
        existing_type=sa.String(length=36),
        nullable=True,
    )
