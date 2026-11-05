"""Owner-scoped paper order request identity.

Revision ID: nv_paper_order_idempotency_v1
Revises: neuro_improvement_journal_v1

This migration intentionally retains legacy rows.
It does not backfill or alter historical financial records.
"""

from alembic import op
import sqlalchemy as sa


revision = "nv_paper_order_idempotency_v1"
down_revision = "neuro_improvement_journal_v1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "order_history",
        sa.Column(
            "request_id",
            sa.String(length=36),
            nullable=True,
        ),
    )
    op.add_column(
        "order_history",
        sa.Column(
            "request_fingerprint",
            sa.String(length=64),
            nullable=True,
        ),
    )
    op.create_unique_constraint(
        "uq_order_history_user_request",
        "order_history",
        ["user_id", "request_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_order_history_user_request",
        "order_history",
        type_="unique",
    )
    op.drop_column(
        "order_history",
        "request_fingerprint",
    )
    op.drop_column(
        "order_history",
        "request_id",
    )
