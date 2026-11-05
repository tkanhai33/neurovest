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


class SnapTradeExternalBalance(
    Base
):
    """
    Durable owner-scoped representation of one external
    SnapTrade account/currency cash balance.

    This table is deliberately separate from PortfolioInventory.

    It:
      * contains no order capability,
      * contains no execution capability,
      * contains no provider secret,
      * stores only hashed broker account identity,
      * remains read-only brokerage information.
    """

    __tablename__ = (
        "snaptrade_external_balances"
    )

    __table_args__ = (
        UniqueConstraint(
            "neurovest_user_id",
            "account_id_hash",
            "currency",
            name=(
                "uq_snaptrade_external_balance_"
                "owner_account_currency"
            ),
        ),
        Index(
            "ix_snaptrade_external_balance_owner",
            "neurovest_user_id",
        ),
        Index(
            "ix_snaptrade_external_balance_account",
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

    currency: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
    )

    cash_amount: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(
            precision=38,
            scale=18,
        ),
        nullable=True,
    )

    buying_power: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(
            precision=38,
            scale=18,
        ),
        nullable=True,
    )

    cash_available: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(
            precision=38,
            scale=18,
        ),
        nullable=True,
    )

    settled_cash: Mapped[
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

    last_synced_at: Mapped[datetime] = mapped_column(
        DateTime(
            timezone=True
        ),
        nullable=False,
        default=utc_now,
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
