"""
Approved chat_public conversation service boundary.

Production routes and external consumers must import conversation
operations through this module rather than importing SQLAlchemy,
ORM models, database sessions, or conversation_store directly.

The underlying store remains an internal implementation detail.
"""

from __future__ import annotations

from backend.app.stacks.chat_public.conversation_store import (
    ConversationStore,
    conversation_store,
    healthcheck,
    utc_now,
)

__all__ = [
    "ConversationStore",
    "conversation_store",
    "healthcheck",
    "utc_now",
]
