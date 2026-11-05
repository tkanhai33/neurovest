from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    Index,
    Numeric,
    String,
    UniqueConstraint,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from backend.app.stacks.db_runtime.database import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class SnapTradeExternalPortfolioValueObservation(Base):

    __tablename__ = (
        "snaptrade_external_portfolio_value_observations"
    )

    __table_args__ = (
        UniqueConstraint(
            "neurovest_user_id",
            "observed_at",
            name="uq_snaptrade_portfolio_value_owner_time",
        ),
        Index(
            "ix_snaptrade_portfolio_value_owner",
            "neurovest_user_id",
        ),
        Index(
            "ix_snaptrade_portfolio_value_owner_time",
            "neurovest_user_id",
            "observed_at",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    neurovest_user_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
    )

    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    market_value: Mapped[Decimal] = mapped_column(
        Numeric(38, 18),
        nullable=False,
    )

    cash: Mapped[Decimal] = mapped_column(
        Numeric(38, 18),
        nullable=False,
    )

    account_value: Mapped[Decimal] = mapped_column(
        Numeric(38, 18),
        nullable=False,
    )

    unrealized_gain: Mapped[Decimal | None] = mapped_column(
        Numeric(38, 18),
        nullable=True,
    )

    source_provider: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="snaptrade",
    )

    read_only: Mapped[bool] = mapped_column(
        Boolean(),
        nullable=False,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
