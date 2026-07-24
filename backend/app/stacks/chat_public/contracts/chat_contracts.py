"""
134A_CHAT_THREAD_AND_MEMORY_CONTRACT

Canonical contracts for NeuroVest conversation threads, messages,
conversation state, memory facts, tool evidence, requests, and responses.

This phase defines structure only.

It does not:
- persist conversations
- alter Ollama prompts
- add streaming
- execute tools
- change broker or trading state
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


ChatRole = Literal[
    "system",
    "user",
    "assistant",
    "tool",
]

ThreadStatus = Literal[
    "active",
    "archived",
]

MemoryStatus = Literal[
    "active",
    "superseded",
    "retracted",
]

EvidenceStatus = Literal[
    "success",
    "error",
    "unavailable",
]

ToolTruthState = Literal[
    "grounded",
    "partial",
    "ungrounded",
    "not_required",
]


def utc_now() -> datetime:
    return datetime.now(UTC)


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex}"


class ChatThread(BaseModel):
    thread_id: str = Field(
        default_factory=lambda: new_id("thread")
    )

    user_id: str | None = None
    title: str | None = None

    status: ThreadStatus = "active"

    summary: str | None = None
    message_count: int = 0

    created_at: datetime = Field(
        default_factory=utc_now
    )

    updated_at: datetime = Field(
        default_factory=utc_now
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class ChatMessage(BaseModel):
    message_id: str = Field(
        default_factory=lambda: new_id("message")
    )

    thread_id: str

    parent_message_id: str | None = None

    role: ChatRole
    content: str

    intent: str | None = None
    symbol: str | None = None

    provider: str | None = None
    model: str | None = None

    tool_evidence_ids: list[str] = Field(
        default_factory=list
    )

    created_at: datetime = Field(
        default_factory=utc_now
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class PendingConversationTask(BaseModel):
    task_id: str = Field(
        default_factory=lambda: new_id("task")
    )

    task_type: str
    description: str

    status: Literal[
        "pending",
        "running",
        "completed",
        "failed",
        "cancelled",
    ] = "pending"

    source_message_id: str | None = None

    details: dict[str, Any] = Field(
        default_factory=dict
    )


class ConversationState(BaseModel):
    thread_id: str

    summary: str = ""

    active_entities: dict[str, Any] = Field(
        default_factory=dict
    )

    active_strategy: dict[str, Any] | None = None

    portfolio_context: dict[str, Any] = Field(
        default_factory=dict
    )

    pending_tasks: list[PendingConversationTask] = Field(
        default_factory=list
    )

    remembered_terms: dict[str, str] = Field(
        default_factory=dict
    )

    last_message_id: str | None = None

    updated_at: datetime = Field(
        default_factory=utc_now
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class MemoryFact(BaseModel):
    memory_id: str = Field(
        default_factory=lambda: new_id("memory")
    )

    thread_id: str

    key: str
    value: Any

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    status: MemoryStatus = "active"

    source_message_id: str | None = None

    created_at: datetime = Field(
        default_factory=utc_now
    )

    updated_at: datetime = Field(
        default_factory=utc_now
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class ToolEvidence(BaseModel):
    evidence_id: str = Field(
        default_factory=lambda: new_id("evidence")
    )

    thread_id: str

    tool_name: str
    tool_call_id: str | None = None

    claim_types: list[str] = Field(
        default_factory=list
    )

    request: dict[str, Any] = Field(
        default_factory=dict
    )

    result: dict[str, Any] = Field(
        default_factory=dict
    )

    status: EvidenceStatus

    observed_at: datetime = Field(
        default_factory=utc_now
    )

    expires_at: datetime | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1
    )

    thread_id: str | None = None
    parent_message_id: str | None = None
    client_message_id: str | None = None

    stream: bool = False

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class ChatResponse(BaseModel):
    status: Literal[
        "ok",
        "error",
        "blocked",
    ]

    thread_id: str

    user_message_id: str
    assistant_message_id: str | None = None

    message: str

    intent: str | None = None
    symbol: str | None = None

    provider: str | None = None
    model: str | None = None

    tool_truth_state: ToolTruthState = (
        "not_required"
    )

    evidence: list[ToolEvidence] = Field(
        default_factory=list
    )

    memory_updates: list[MemoryFact] = Field(
        default_factory=list
    )

    conversation_state: ConversationState | None = None

    error: str | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


CHAT_CONTRACT_VERSION = "134A.v1"
