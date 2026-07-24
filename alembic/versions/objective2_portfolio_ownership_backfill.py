"""Assign legacy portfolio data to the development account.

Revision ID: objective2_portfolio_owner
Revises: iqc_s5b_access_token_revocations
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "objective2_portfolio_owner"

down_revision: str | Sequence[str] | None = (
    "iqc_s5b_access_token_revocations"
)

branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


DEV_USER_ID = (
    "28d5c922-3114-4a99-9f14-1a4c25335e3d"
)

DEV_EMAIL = "dev@neurovest.com"


def upgrade() -> None:
    bind = op.get_bind()

    owner = bind.execute(
        sa.text(
            """
            SELECT
                id,
                email_normalized
            FROM identity_users
            WHERE id = :user_id
            """
        ),
        {
            "user_id": DEV_USER_ID,
        },
    ).mappings().one_or_none()

    if owner is None:
        raise RuntimeError(
            "Development ownership account does not exist"
        )

    if owner["email_normalized"] != DEV_EMAIL:
        raise RuntimeError(
            "Development ownership account email mismatch"
        )

    op.add_column(
        "order_history",
        sa.Column(
            "user_id",
            sa.String(length=36),
            nullable=True,
        ),
    )

    op.add_column(
        "portfolio_inventory",
        sa.Column(
            "user_id",
            sa.String(length=36),
            nullable=True,
        ),
    )

    bind.execute(
        sa.text(
            """
            UPDATE order_history
            SET user_id = :user_id
            WHERE user_id IS NULL
            """
        ),
        {
            "user_id": DEV_USER_ID,
        },
    )

    bind.execute(
        sa.text(
            """
            UPDATE portfolio_inventory
            SET user_id = :user_id
            WHERE user_id IS NULL
            """
        ),
        {
            "user_id": DEV_USER_ID,
        },
    )

    order_null_count = bind.execute(
        sa.text(
            """
            SELECT count(*)
            FROM order_history
            WHERE user_id IS NULL
            """
        )
    ).scalar_one()

    inventory_null_count = bind.execute(
        sa.text(
            """
            SELECT count(*)
            FROM portfolio_inventory
            WHERE user_id IS NULL
            """
        )
    ).scalar_one()

    if order_null_count != 0:
        raise RuntimeError(
            "Order ownership backfill left NULL rows"
        )

    if inventory_null_count != 0:
        raise RuntimeError(
            "Inventory ownership backfill left NULL rows"
        )

    op.create_foreign_key(
        "fk_order_history_user_id_identity_users",
        "order_history",
        "identity_users",
        [
            "user_id",
        ],
        [
            "id",
        ],
        ondelete="CASCADE",
    )

    op.create_foreign_key(
        "fk_portfolio_inventory_user_id_identity_users",
        "portfolio_inventory",
        "identity_users",
        [
            "user_id",
        ],
        [
            "id",
        ],
        ondelete="CASCADE",
    )

    op.create_index(
        "ix_order_history_user_id",
        "order_history",
        [
            "user_id",
        ],
        unique=False,
    )

    op.create_index(
        "ix_portfolio_inventory_user_id",
        "portfolio_inventory",
        [
            "user_id",
        ],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_portfolio_inventory_user_id",
        table_name="portfolio_inventory",
    )

    op.drop_index(
        "ix_order_history_user_id",
        table_name="order_history",
    )

    op.drop_constraint(
        "fk_portfolio_inventory_user_id_identity_users",
        "portfolio_inventory",
        type_="foreignkey",
    )

    op.drop_constraint(
        "fk_order_history_user_id_identity_users",
        "order_history",
        type_="foreignkey",
    )

    op.drop_column(
        "portfolio_inventory",
        "user_id",
    )

    op.drop_column(
        "order_history",
        "user_id",
    )
