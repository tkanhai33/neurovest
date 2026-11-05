from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Index,
    String,
    UniqueConstraint,
    func,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from backend.app.stacks.db_runtime.database import Base


class UserStrategyActivation(Base):
    """
    Persistent user preference over the reference strategy catalog.

    This is selection metadata only. It does not authorize strategy
    execution, model inference, promotion, training, or broker activity.
    """

    __tablename__ = "user_strategy_activations"

    __table_args__ = (
        UniqueConstraint(
            "owner_subject",
            "strategy_name",
            name="uq_user_strategy_activation_owner_strategy",
        ),
        Index(
            "ix_user_strategy_activation_owner_enabled",
            "owner_subject",
            "enabled",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    owner_subject: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    strategy_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class UserStrategyUniverseMember(Base):
    """
    Owner-scoped daily-OHLCV universe membership.

    This stores data-selection metadata only. It does not enable a strategy,
    authorize execution, or create broker activity.
    """

    __tablename__ = "user_strategy_universe_members"

    __table_args__ = (
        UniqueConstraint(
            "owner_subject",
            "universe_name",
            "symbol",
            name="uq_user_strategy_universe_owner_name_symbol",
        ),
        Index(
            "ix_user_strategy_universe_owner_name",
            "owner_subject",
            "universe_name",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    owner_subject: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    universe_name: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default="default",
        server_default="default",
    )

    symbol: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
