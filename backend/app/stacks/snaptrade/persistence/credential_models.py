from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    LargeBinary,
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
    return datetime.now(UTC)


class SnapTradeUserCredential(Base):
    """
    Owner-scoped encrypted SnapTrade user credential.

    The plaintext SnapTrade userSecret is never persisted.
    """

    __tablename__ = "snaptrade_user_credentials"

    __table_args__ = (
        UniqueConstraint(
            "neurovest_user_id",
            name=(
                "uq_snaptrade_user_credentials_"
                "neurovest_user_id"
            ),
        ),
        UniqueConstraint(
            "snaptrade_user_id",
            name=(
                "uq_snaptrade_user_credentials_"
                "snaptrade_user_id"
            ),
        ),
        Index(
            "ix_snaptrade_user_credentials_owner",
            "neurovest_user_id",
        ),
        Index(
            "ix_snaptrade_user_credentials_status",
            "connection_status",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    neurovest_user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "identity_users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    snaptrade_user_id: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    encrypted_user_secret: Mapped[bytes] = mapped_column(
        LargeBinary,
        nullable=False,
    )

    encryption_key_version: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="v1",
    )

    connection_status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="registered",
    )

    last_sync_status: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )
