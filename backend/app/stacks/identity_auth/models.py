from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from backend.app.stacks.db_runtime.database import (
    Base,
)


def utc_now() -> datetime:
    return datetime.now(
        UTC
    )


class IdentityUser(Base):
    __tablename__ = "identity_users"

    __table_args__ = (
        UniqueConstraint(
            "email_normalized",
            name="uq_identity_users_email_normalized",
        ),
        Index(
            "ix_identity_users_status",
            "status",
        ),
        Index(
            "ix_identity_users_role",
            "role",
        ),
        Index(
            "ix_identity_users_subscription_tier",
            "subscription_tier",
        ),
        CheckConstraint(
            "role IN ('user', 'admin', 'owner')",
            name="ck_identity_users_role",
        ),
        CheckConstraint(
            "subscription_tier IN "
            "('free', 'basic', 'pro', 'elite', "
            "'enterprise', 'internal')",
            name="ck_identity_users_subscription_tier",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(
            uuid4()
        ),
    )

    email_normalized: Mapped[str] = mapped_column(
        String(320),
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="active",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    role: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="user",
        server_default="user",
    )

    subscription_tier: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="free",
        server_default="free",
    )

    must_change_password: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    display_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
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

    refresh_sessions: Mapped[
        list[
            "IdentityRefreshSession"
        ]
    ] = relationship(
        back_populates="user",
        cascade=(
            "all, delete-orphan"
        ),
        passive_deletes=True,
    )


class IdentityRefreshSession(Base):
    __tablename__ = (
        "identity_refresh_sessions"
    )

    __table_args__ = (
        UniqueConstraint(
            "token_id",
            name=(
                "uq_identity_refresh_sessions_"
                "token_id"
            ),
        ),
        Index(
            "ix_identity_refresh_sessions_"
            "user_active",
            "user_id",
            "revoked_at",
            "expires_at",
        ),
        Index(
            "ix_identity_refresh_sessions_"
            "family",
            "family_id",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(
            uuid4()
        ),
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "identity_users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    token_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    token_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    family_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
    )

    issued_at: Mapped[datetime] = mapped_column(
        DateTime(
            timezone=True
        ),
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(
            timezone=True
        ),
        nullable=False,
    )

    revoked_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(
            timezone=True
        ),
        nullable=True,
    )

    replaced_by: Mapped[
        str | None
    ] = mapped_column(
        String(64),
        nullable=True,
    )

    last_used_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(
            timezone=True
        ),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(
            timezone=True
        ),
        nullable=False,
        default=utc_now,
    )

    user: Mapped[IdentityUser] = relationship(
        back_populates="refresh_sessions",
    )
