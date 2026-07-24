from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    DateTime,
    Index,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from backend.app.stacks.identity_auth.models import (
    Base,
)


def utc_now_naive() -> datetime:
    return datetime.now(
        UTC
    ).replace(
        tzinfo=None
    )


class IdentityAccessTokenRevocation(Base):
    """
    Durable access-token revocation record.

    The record stores only a JWT identifier and safe lifecycle
    metadata. Raw JWT values, token hashes, passwords, and refresh
    credentials are intentionally excluded.
    """

    __tablename__ = (
        "identity_access_token_revocations"
    )

    __table_args__ = (
        UniqueConstraint(
            "token_id",
            name=(
                "uq_identity_access_token_"
                "revocations_token_id"
            ),
        ),
        Index(
            "ix_identity_access_token_"
            "revocations_user_id",
            "user_id",
        ),
        Index(
            "ix_identity_access_token_"
            "revocations_expires_at",
            "expires_at",
        ),
        Index(
            "ix_identity_access_token_"
            "revocations_revoked_at",
            "revoked_at",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(
            uuid.uuid4()
        ),
    )

    token_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
    )

    issued_at: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
    )

    revoked_at: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
        default=utc_now_naive,
    )

    reason: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default="logout",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
        default=utc_now_naive,
    )
