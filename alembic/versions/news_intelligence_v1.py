"""news intelligence v1

Revision ID: news_intelligence_v1
Revises: snaptrade_external_balance_v1
Create Date: 20260828_112541
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "news_intelligence_v1"
down_revision: Union[str, None] = "snaptrade_external_balance_v1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        "news_intelligence_records",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "symbol",
            sa.String(
                length=32,
            ),
            nullable=True,
        ),

        sa.Column(
            "headline",
            sa.String(
                length=512,
            ),
            nullable=False,
        ),

        sa.Column(
            "summary",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "source_name",
            sa.String(
                length=128,
            ),
            nullable=True,
        ),

        sa.Column(
            "source_url",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "published_at",
            sa.DateTime(
                timezone=True,
            ),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(
                timezone=True,
            ),
            server_default=sa.text(
                "now()"
            ),
            nullable=False,
        ),

        sa.PrimaryKeyConstraint(
            "id"
        ),
    )

    op.create_index(
        "ix_news_intelligence_records_symbol",
        "news_intelligence_records",
        [
            "symbol",
        ],
        unique=False,
    )

    op.create_index(
        "ix_news_intelligence_records_published_at",
        "news_intelligence_records",
        [
            "published_at",
        ],
        unique=False,
    )


def downgrade() -> None:

    op.drop_index(
        "ix_news_intelligence_records_published_at",
        table_name="news_intelligence_records",
    )

    op.drop_index(
        "ix_news_intelligence_records_symbol",
        table_name="news_intelligence_records",
    )

    op.drop_table(
        "news_intelligence_records"
    )
