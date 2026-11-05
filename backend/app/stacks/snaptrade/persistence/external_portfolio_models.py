from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import (
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

from backend.app.stacks.db_runtime.database import (
    Base,
)


def utc_now() -> datetime:
    return datetime.now(
        UTC
    )


class SnapTradeExternalPortfolioPosition(
    Base
):
    """
    Durable owner-scoped representation of an external SnapTrade
    brokerage position.

    This table is deliberately separate from PortfolioInventory.

    PortfolioInventory remains NeuroVest paper/execution inventory.

    This model:
      * contains no order capability,
      * contains no execution capability,
      * contains no provider secrets,
      * stores hashed account/position identifiers only,
      * is scoped to one authenticated NeuroVest owner.
    """

    __tablename__ = (
        "snaptrade_external_portfolio_positions"
    )

    __table_args__ = (
        UniqueConstraint(
            "neurovest_user_id",
            "account_id_hash",
            "position_id_hash",
            name=(
                "uq_snaptrade_external_position_"
                "owner_account_position"
            ),
        ),
        Index(
            "ix_snaptrade_external_position_owner",
            "neurovest_user_id",
        ),
        Index(
            "ix_snaptrade_external_position_owner_symbol",
            "neurovest_user_id",
            "symbol",
        ),
        Index(
            "ix_snaptrade_external_position_account",
            "account_id_hash",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(
            uuid4()
        ),
    )

    neurovest_user_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
    )

    account_id_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    position_id_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    symbol: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    instrument_kind: Mapped[str | None] = (
        mapped_column(
            String(64),
            nullable=True,
        )
    )

    currency: Mapped[str | None] = mapped_column(
        String(16),
        nullable=True,
    )

    shares_quantity: Mapped[Decimal] = (
        mapped_column(
            Numeric(
                precision=38,
                scale=18,
            ),
            nullable=False,
        )
    )

    average_entry_price: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(
            precision=38,
            scale=18,
        ),
        nullable=True,
    )

    current_price: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(
            precision=38,
            scale=18,
        ),
        nullable=True,
    )

    market_value: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(
            precision=38,
            scale=18,
        ),
        nullable=True,
    )

    total_cost_basis: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(
            precision=38,
            scale=18,
        ),
        nullable=True,
    )

    unrealized_gain: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(
            precision=38,
            scale=18,
        ),
        nullable=True,
    )

    source_provider: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="snaptrade",
    )

    read_only: Mapped[bool] = mapped_column(
        nullable=False,
        default=True,
    )

    last_synced_at: Mapped[datetime] = (
        mapped_column(
            DateTime(
                timezone=True
            ),
            nullable=False,
            default=utc_now,
        )
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(
            timezone=True
        ),
        nullable=False,
        default=utc_now,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(
            timezone=True
        ),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )
