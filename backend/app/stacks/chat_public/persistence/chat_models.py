"""
134B2_CHAT_PERSISTENCE_MODELS

Canonical SQLAlchemy persistence models for NeuroVest conversations.

Owned tables:
- chat_threads
- chat_messages
- chat_conversation_states
- chat_memory_facts
- chat_tool_evidence

This phase defines and registers persistence models.

It does not:
- change the live chat API
- save live chat messages
- assemble conversation context
- modify Ollama prompts
- enable streaming
- execute financial tools
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.stacks.db_runtime.database import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex}"


class ChatThreadRecord(Base):
    __tablename__ = "chat_threads"

    thread_id: Mapped[str] = mapped_column(
        String(80),
        primary_key=True,
        default=lambda: new_id("thread"),
    )

    user_id: Mapped[str | None] = mapped_column(
        String(160),
        nullable=True,
        index=True,
    )

    title: Mapped[str | None] = mapped_column(
        String(300),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="active",
        index=True,
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    message_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        index=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
        index=True,
    )

    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    __table_args__ = (
        Index(
            "ix_chat_threads_status_updated",
            "status",
            "updated_at",
        ),
    )


class ChatMessageRecord(Base):
    __tablename__ = "chat_messages"

    message_id: Mapped[str] = mapped_column(
        String(80),
        primary_key=True,
        default=lambda: new_id("message"),
    )

    thread_id: Mapped[str] = mapped_column(
        String(80),
        ForeignKey(
            "chat_threads.thread_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    parent_message_id: Mapped[str | None] = mapped_column(
        String(80),
        ForeignKey(
            "chat_messages.message_id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    client_message_id: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
        index=True,
    )

    role: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    intent: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
        index=True,
    )

    symbol: Mapped[str | None] = mapped_column(
        String(40),
        nullable=True,
        index=True,
    )

    provider: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True,
    )

    model: Mapped[str | None] = mapped_column(
        String(160),
        nullable=True,
    )

    tool_evidence_ids: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        index=True,
    )

    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    __table_args__ = (
        Index(
            "ix_chat_messages_thread_created",
            "thread_id",
            "created_at",
        ),
        Index(
            "ix_chat_messages_thread_role",
            "thread_id",
            "role",
        ),
    )


class ConversationStateRecord(Base):
    __tablename__ = "chat_conversation_states"

    thread_id: Mapped[str] = mapped_column(
        String(80),
        ForeignKey(
            "chat_threads.thread_id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    active_entities: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    active_strategy: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    portfolio_context: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    pending_tasks: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    remembered_terms: Mapped[dict[str, str]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    last_message_id: Mapped[str | None] = mapped_column(
        String(80),
        ForeignKey(
            "chat_messages.message_id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
        index=True,
    )

    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )


class MemoryFactRecord(Base):
    __tablename__ = "chat_memory_facts"

    memory_id: Mapped[str] = mapped_column(
        String(80),
        primary_key=True,
        default=lambda: new_id("memory"),
    )

    thread_id: Mapped[str] = mapped_column(
        String(80),
        ForeignKey(
            "chat_threads.thread_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    key: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
        index=True,
    )

    value_json: Mapped[Any] = mapped_column(
        JSON,
        nullable=False,
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
    )

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="active",
        index=True,
    )

    source_message_id: Mapped[str | None] = mapped_column(
        String(80),
        ForeignKey(
            "chat_messages.message_id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        index=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
        index=True,
    )

    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    __table_args__ = (
        Index(
            "ix_chat_memory_thread_key_status",
            "thread_id",
            "key",
            "status",
        ),
    )


class ToolEvidenceRecord(Base):
    __tablename__ = "chat_tool_evidence"

    evidence_id: Mapped[str] = mapped_column(
        String(80),
        primary_key=True,
        default=lambda: new_id("evidence"),
    )

    thread_id: Mapped[str] = mapped_column(
        String(80),
        ForeignKey(
            "chat_threads.thread_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    tool_name: Mapped[str] = mapped_column(
        String(180),
        nullable=False,
        index=True,
    )

    tool_call_id: Mapped[str | None] = mapped_column(
        String(160),
        nullable=True,
        index=True,
    )

    claim_types: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    request_json: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    result_json: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
    )

    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        index=True,
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    __table_args__ = (
        Index(
            "ix_chat_evidence_thread_observed",
            "thread_id",
            "observed_at",
        ),
        Index(
            "ix_chat_evidence_tool_status",
            "tool_name",
            "status",
        ),
    )


CHAT_PERSISTENCE_TABLES = (
    "chat_threads",
    "chat_messages",
    "chat_conversation_states",
    "chat_memory_facts",
    "chat_tool_evidence",
)
