"""SnapTrade portfolio value history.

Revision ID: snaptrade_value_hist_v1
Revises: support_ticketing_v1
"""

from alembic import op
import sqlalchemy as sa


revision = "snaptrade_value_hist_v1"
down_revision = "support_ticketing_v1"
branch_labels = None
depends_on = None


def upgrade() -> None:

    op.create_table(
        "snaptrade_external_portfolio_value_observations",

        sa.Column(
            "id",
            sa.String(length=36),
            nullable=False,
        ),

        sa.Column(
            "neurovest_user_id",
            sa.String(length=36),
            nullable=False,
        ),

        sa.Column(
            "observed_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.Column(
            "market_value",
            sa.Numeric(38, 18),
            nullable=False,
        ),

        sa.Column(
            "cash",
            sa.Numeric(38, 18),
            nullable=False,
        ),

        sa.Column(
            "account_value",
            sa.Numeric(38, 18),
            nullable=False,
        ),

        sa.Column(
            "unrealized_gain",
            sa.Numeric(38, 18),
            nullable=True,
        ),

        sa.Column(
            "source_provider",
            sa.String(length=32),
            nullable=False,
            server_default="snaptrade",
        ),

        sa.Column(
            "read_only",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),

        sa.PrimaryKeyConstraint(
            "id"
        ),

        sa.UniqueConstraint(
            "neurovest_user_id",
            "observed_at",
            name="uq_snaptrade_portfolio_value_owner_time",
        ),
    )

    op.create_index(
        "ix_snaptrade_portfolio_value_owner",
        "snaptrade_external_portfolio_value_observations",
        [
            "neurovest_user_id",
        ],
    )

    op.create_index(
        "ix_snaptrade_portfolio_value_owner_time",
        "snaptrade_external_portfolio_value_observations",
        [
            "neurovest_user_id",
            "observed_at",
        ],
    )

    op.execute(
        """
        GRANT SELECT, INSERT
        ON TABLE snaptrade_external_portfolio_value_observations
        TO neurovest
        """
    )


def downgrade() -> None:

    op.execute(
        """
        REVOKE SELECT, INSERT
        ON TABLE snaptrade_external_portfolio_value_observations
        FROM neurovest
        """
    )

    op.drop_index(
        "ix_snaptrade_portfolio_value_owner_time",
        table_name="snaptrade_external_portfolio_value_observations",
    )

    op.drop_index(
        "ix_snaptrade_portfolio_value_owner",
        table_name="snaptrade_external_portfolio_value_observations",
    )

    op.drop_table(
        "snaptrade_external_portfolio_value_observations"
    )
