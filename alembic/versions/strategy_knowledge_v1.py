"""Create authoritative strategy knowledge repository.

Revision ID: strategy_knowledge_v1
Revises: snaptrade_external_inventory_v1
"""

from alembic import op
import sqlalchemy as sa


revision = "strategy_knowledge_v1"
down_revision = "snaptrade_external_inventory_v1"
branch_labels = None
depends_on = None


def upgrade() -> None:

    op.create_table(
        "strategy_knowledge",

        sa.Column(
            "id",
            sa.Uuid(),
            primary_key=True,
            nullable=False,
        ),

        sa.Column(
            "strategy_id",
            sa.String(length=128),
            nullable=False,
        ),

        sa.Column(
            "strategy_version",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "strategy_fingerprint",
            sa.String(length=128),
            nullable=False,
        ),

        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "strategy_family",
            sa.String(length=128),
            nullable=True,
        ),

        sa.Column(
            "rules",
            sa.JSON(),
            nullable=False,
        ),

        sa.Column(
            "entry_rules",
            sa.JSON(),
            nullable=False,
        ),

        sa.Column(
            "exit_rules",
            sa.JSON(),
            nullable=False,
        ),

        sa.Column(
            "risk_rules",
            sa.JSON(),
            nullable=False,
        ),

        sa.Column(
            "parameters",
            sa.JSON(),
            nullable=False,
        ),

        sa.Column(
            "symbols",
            sa.JSON(),
            nullable=False,
        ),

        sa.Column(
            "provider_symbols",
            sa.JSON(),
            nullable=False,
        ),

        sa.Column(
            "asset_class",
            sa.String(length=64),
            nullable=True,
        ),

        sa.Column(
            "generation_source",
            sa.String(length=128),
            nullable=True,
        ),

        sa.Column(
            "generation_run_id",
            sa.String(length=255),
            nullable=True,
        ),

        sa.Column(
            "parent_strategy_id",
            sa.String(length=128),
            nullable=True,
        ),

        sa.Column(
            "parent_strategy_version",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "created_from_candidate_id",
            sa.String(length=128),
            nullable=True,
        ),

        sa.Column(
            "dataset_identifiers",
            sa.JSON(),
            nullable=False,
        ),

        sa.Column(
            "history_start",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.Column(
            "history_end",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.Column(
            "history_row_count",
            sa.BigInteger(),
            nullable=True,
        ),

        sa.Column(
            "history_digest",
            sa.String(length=128),
            nullable=True,
        ),

        sa.Column(
            "feature_contract",
            sa.String(length=255),
            nullable=True,
        ),

        sa.Column(
            "feature_count",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "feature_digest",
            sa.String(length=128),
            nullable=True,
        ),

        sa.Column(
            "frozen25_participation",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),

        sa.Column(
            "model_contract",
            sa.String(length=255),
            nullable=True,
        ),

        sa.Column(
            "validation_status",
            sa.String(length=64),
            nullable=True,
        ),

        sa.Column(
            "scorecard",
            sa.JSON(),
            nullable=False,
        ),

        sa.Column(
            "backtest_metrics",
            sa.JSON(),
            nullable=False,
        ),

        sa.Column(
            "forward_metrics",
            sa.JSON(),
            nullable=False,
        ),

        sa.Column(
            "risk_metrics",
            sa.JSON(),
            nullable=False,
        ),

        sa.Column(
            "acceptance_thresholds",
            sa.JSON(),
            nullable=False,
        ),

        sa.Column(
            "rejection_reasons",
            sa.JSON(),
            nullable=False,
        ),

        sa.Column(
            "lifecycle_state",
            sa.String(length=64),
            nullable=False,
        ),

        sa.Column(
            "admission_decision",
            sa.String(length=64),
            nullable=True,
        ),

        sa.Column(
            "admitted_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.Column(
            "admission_reason",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "promotion_status",
            sa.String(length=64),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),

        sa.Column(
            "created_by",
            sa.String(length=255),
            nullable=True,
        ),

        sa.Column(
            "source_evidence",
            sa.JSON(),
            nullable=False,
        ),

        sa.UniqueConstraint(
            "strategy_id",
            "strategy_version",
            name="uq_strategy_knowledge_id_version",
        ),

        sa.UniqueConstraint(
            "strategy_fingerprint",
            name="uq_strategy_knowledge_fingerprint",
        ),
    )


    op.create_index(
        "ix_strategy_knowledge_strategy_id",
        "strategy_knowledge",
        ["strategy_id"],
        unique=False,
    )


    op.create_index(
        "ix_strategy_knowledge_lifecycle_state",
        "strategy_knowledge",
        ["lifecycle_state"],
        unique=False,
    )


def downgrade() -> None:

    op.drop_index(
        "ix_strategy_knowledge_lifecycle_state",
        table_name="strategy_knowledge",
    )

    op.drop_index(
        "ix_strategy_knowledge_strategy_id",
        table_name="strategy_knowledge",
    )

    op.drop_table(
        "strategy_knowledge"
    )
