"""Add first-class strategy_name to strategy_knowledge.

Revision ID: strategy_knowledge_strategy_name_v1
Revises: strategy_knowledge_v1
"""

from alembic import op
import sqlalchemy as sa


revision = 'strategy_knowledge_name_v1'
down_revision = "strategy_knowledge_v1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "strategy_knowledge",
        sa.Column(
            "strategy_name",
            sa.String(length=255),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "strategy_knowledge",
        "strategy_name",
    )
