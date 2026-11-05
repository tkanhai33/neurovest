from __future__ import annotations

from datetime import (
    UTC,
    datetime,
)
from uuid import uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
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


class SupportTicket(
    Base,
):
    __tablename__ = (
        "support_tickets"
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ("
            "'OPEN', "
            "'WAITING_FOR_USER', "
            "'WAITING_FOR_ADMINISTRATOR', "
            "'RESOLVED', "
            "'CLOSED'"
            ")",
            name=(
                "ck_support_tickets_status"
            ),
        ),

        CheckConstraint(
            "priority IN ("
            "'LOW', "
            "'NORMAL', "
            "'HIGH', "
            "'URGENT'"
            ")",
            name=(
                "ck_support_tickets_priority"
            ),
        ),

        Index(
            "ix_support_tickets_owner_user_id",
            "owner_user_id",
        ),

        Index(
            "ix_support_tickets_status",
            "status",
        ),

        Index(
            "ix_support_tickets_updated_at",
            "updated_at",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(
            36
        ),
        primary_key=True,
        default=lambda: str(
            uuid4()
        ),
    )

    owner_user_id: Mapped[str] = mapped_column(
        String(
            36
        ),
        ForeignKey(
            "identity_users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    subject: Mapped[str] = mapped_column(
        String(
            255
        ),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(
            32
        ),
        nullable=False,
        default="OPEN",
        server_default="OPEN",
    )

    priority: Mapped[str] = mapped_column(
        String(
            32
        ),
        nullable=False,
        default="NORMAL",
        server_default="NORMAL",
    )

    created_at: Mapped[
        datetime
    ] = mapped_column(
        DateTime(
            timezone=True
        ),
        nullable=False,
        default=utc_now,
    )

    updated_at: Mapped[
        datetime
    ] = mapped_column(
        DateTime(
            timezone=True
        ),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    resolved_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(
            timezone=True
        ),
        nullable=True,
    )

    closed_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(
            timezone=True
        ),
        nullable=True,
    )

    messages: Mapped[
        list[
            "SupportTicketMessage"
        ]
    ] = relationship(
        back_populates="ticket",
        cascade=(
            "all, delete-orphan"
        ),
        passive_deletes=True,
        order_by=(
            "SupportTicketMessage.created_at"
        ),
    )


class SupportTicketMessage(
    Base,
):
    __tablename__ = (
        "support_ticket_messages"
    )

    __table_args__ = (
        CheckConstraint(
            "author_role IN ("
            "'USER', "
            "'ADMINISTRATOR'"
            ")",
            name=(
                "ck_support_ticket_messages_author_role"
            ),
        ),

        Index(
            "ix_support_ticket_messages_ticket_id",
            "ticket_id",
        ),

        Index(
            "ix_support_ticket_messages_created_at",
            "created_at",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(
            36
        ),
        primary_key=True,
        default=lambda: str(
            uuid4()
        ),
    )

    ticket_id: Mapped[str] = mapped_column(
        String(
            36
        ),
        ForeignKey(
            "support_tickets.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    author_user_id: Mapped[str] = mapped_column(
        String(
            36
        ),
        ForeignKey(
            "identity_users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    author_role: Mapped[str] = mapped_column(
        String(
            32
        ),
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        Text(),
        nullable=False,
    )

    created_at: Mapped[
        datetime
    ] = mapped_column(
        DateTime(
            timezone=True
        ),
        nullable=False,
        default=utc_now,
    )

    ticket: Mapped[
        SupportTicket
    ] = relationship(
        back_populates="messages",
    )
