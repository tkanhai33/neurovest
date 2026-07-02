from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class AiChatRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class AiToolRequestStatus(StrEnum):
    DISABLED = "disabled"
    DENIED = "denied"
    SKELETON_ONLY = "skeleton_only"


@dataclass(frozen=True)
class AiChatMessageContract:
    message_id: str
    role: AiChatRole
    content: str


@dataclass(frozen=True)
class AiChatSessionContract:
    session_id: str
    user_id: str | None = None


@dataclass(frozen=True)
class AiToolRequestContract:
    request_id: str
    tool_name: str
    status: AiToolRequestStatus = AiToolRequestStatus.DISABLED


@dataclass(frozen=True)
class AiChatSkeletonStatus:
    stack: str = "ai_chat"
    phase: str = "phase_12_skeleton"
    ollama_adapter_implemented: bool = False
    model_calls_enabled: bool = False
    rag_implemented: bool = False
    memory_implemented: bool = False
    tool_use_implemented: bool = False
    runtime_integration_implemented: bool = False
    broker_integration_implemented: bool = False
    trading_advice_implemented: bool = False
    business_logic_implemented: bool = False
