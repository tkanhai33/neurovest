"""Owner-scoped paper equity high-water state.

Revision ID: nv_paper_equity_high_water_v1
Revises: nv_paper_order_idempotency_v1

This migration creates an EMPTY persistence table.

No existing accounts are automatically initialized.
No high-water marks are inferred from cash, cost basis,
historical order size, or unverified market values.
"""

from alembic import op
import sqlalchemy as sa


revision = "nv_paper_equity_high_water_v1"
down_revision = "nv_paper_order_idempotency_v1"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "paper_equity_high_water",
        sa.Column(
            "user_id",
            sa.String(),
            sa.ForeignKey(
                "identity_users.id",
                ondelete="CASCADE",
            ),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "currency",
            sa.String(length=3),
            nullable=False,
        ),
        sa.Column(
            "peak_equity",
            sa.Numeric(46, 28),
            nullable=False,
        ),
        sa.Column(
            "revision",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "initialization_source",
            sa.String(length=128),
            nullable=False,
        ),
        sa.Column(
            "initialized_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.CheckConstraint(
            "peak_equity > 0",
            name="ck_paper_equity_high_water_positive_peak",
        ),
        sa.CheckConstraint(
            "revision >= 1",
            name="ck_paper_equity_high_water_revision",
        ),
        sa.CheckConstraint(
            "char_length(currency) = 3",
            name="ck_paper_equity_high_water_currency",
        ),
        sa.CheckConstraint(
            "char_length(initialization_source) > 0",
            name="ck_paper_equity_high_water_source",
        ),
    )


def downgrade():
    op.drop_table("paper_equity_high_water")
