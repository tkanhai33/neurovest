from __future__ import annotations
from sqlalchemy import JSON

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.stacks.db_runtime.database import Base




class StrategyKnowledge(Base):
    __tablename__ = "strategy_knowledge"

    __table_args__ = (
        UniqueConstraint(
            "strategy_id",
            "strategy_version",
            name="uq_strategy_knowledge_strategy_version",
        ),
        UniqueConstraint(
            "strategy_fingerprint",
            name="uq_strategy_knowledge_fingerprint",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    strategy_id: Mapped[str] = mapped_column(
        String(length=128),
        nullable=False,
        index=True,
    )

    strategy_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    strategy_fingerprint: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    strategy_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    strategy_family: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        index=True,
    )

    rules: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    entry_rules: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    exit_rules: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    risk_rules: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    parameters: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    symbols: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    provider_symbols: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    asset_class: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )

    generation_source: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    generation_run_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    parent_strategy_id: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        index=True,
    )

    parent_strategy_version: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    created_from_candidate_id: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        index=True,
    )

    dataset_identifiers: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    history_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    history_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    history_row_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    history_digest: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    feature_contract: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    feature_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    feature_digest: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    frozen25_participation: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    model_contract: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    validation_status: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )

    scorecard: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    backtest_metrics: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    forward_metrics: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    risk_metrics: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    acceptance_thresholds: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    rejection_reasons: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    lifecycle_state: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default="candidate",
        index=True,
    )

    admission_decision: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )

    admitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    admission_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    promotion_status: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )

    created_by: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    source_evidence: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
