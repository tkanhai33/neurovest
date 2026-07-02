#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND="$ROOT/backend"
STACK="$BACKEND/app/stacks/ai_chat"

echo "========================================="
echo "PHASE 12 - AI CHAT SKELETON"
echo "========================================="

cd "$ROOT"

echo "Running baseline tests..."
pytest

mkdir -p "$STACK"/{contracts,domain,services,adapters,api,tests}

cat > "$STACK/contracts/ai_chat_contract.py" <<'EOF'
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
EOF

cat > "$STACK/services/ai_chat_service.py" <<'EOF'
from __future__ import annotations

from app.stacks.ai_chat.contracts.ai_chat_contract import (
    AiChatSkeletonStatus,
    AiToolRequestContract,
    AiToolRequestStatus,
)


def get_ai_chat_skeleton_status() -> AiChatSkeletonStatus:
    return AiChatSkeletonStatus()


def deny_all_ai_tool_requests_in_skeleton(
    request: AiToolRequestContract,
) -> AiToolRequestContract:
    return AiToolRequestContract(
        request_id=request.request_id,
        tool_name=request.tool_name,
        status=AiToolRequestStatus.DENIED,
    )
EOF

cat > "$STACK/api/ai_chat_routes.py" <<'EOF'
from __future__ import annotations

from fastapi import APIRouter

from app.stacks.ai_chat.services.ai_chat_service import (
    get_ai_chat_skeleton_status,
)

router = APIRouter(prefix="/ai-chat", tags=["ai-chat"])


@router.get("/status")
def ai_chat_status() -> dict[str, object]:
    status = get_ai_chat_skeleton_status()
    return {
        "stack": status.stack,
        "phase": status.phase,
        "ollama_adapter_implemented": status.ollama_adapter_implemented,
        "model_calls_enabled": status.model_calls_enabled,
        "rag_implemented": status.rag_implemented,
        "memory_implemented": status.memory_implemented,
        "tool_use_implemented": status.tool_use_implemented,
        "runtime_integration_implemented": status.runtime_integration_implemented,
        "broker_integration_implemented": status.broker_integration_implemented,
        "trading_advice_implemented": status.trading_advice_implemented,
        "business_logic_implemented": status.business_logic_implemented,
    }
EOF

cat > "$STACK/adapters/README.md" <<'EOF'
# AI Chat Adapters

Phase 12 skeleton only.

Future local runtime:
- Ollama

Forbidden:
- real model calls
- tool execution
- runtime execution
- broker calls
- order placement
- trading advice implementation
EOF

cat > "$STACK/adapters/ollama_adapter.py" <<'EOF'
from __future__ import annotations


def ollama_adapter_placeholder() -> str:
    return "phase_12_skeleton_only_no_model_calls"
EOF

cat > "$STACK/domain/README.md" <<'EOF'
# AI Chat Domain

Phase 12 skeleton only.

Allowed:
- chat message contract
- chat session contract
- tool request contract
- skeleton denial service
- status contract

Forbidden:
- real Ollama calls
- RAG implementation
- memory implementation
- tool execution
- runtime orchestration
- broker interaction
- trade placement
EOF

cat > "$STACK/tests/README.md" <<'EOF'
# AI Chat Stack Tests

Phase 12 uses root backend tests for certification.
EOF

cat > "$STACK/README.md" <<'EOF'
# ai_chat

Phase 12 — AI Chat Skeleton.

Owns:
- Neuro chat contracts
- message/session contracts
- future Ollama adapter boundary
- future RAG/memory boundary
- future tool-use boundary

Forbidden in Phase 12:
- real model calls
- RAG implementation
- memory implementation
- tool execution
- runtime execution
- broker interaction
- trading advice implementation
EOF

cat > "$BACKEND/tests/contracts/test_ai_chat_contract.py" <<'EOF'
from app.stacks.ai_chat.contracts.ai_chat_contract import (
    AiChatMessageContract,
    AiChatRole,
    AiChatSessionContract,
    AiChatSkeletonStatus,
    AiToolRequestContract,
    AiToolRequestStatus,
)


def test_ai_chat_message_contract_shape() -> None:
    message = AiChatMessageContract(
        message_id="message_001",
        role=AiChatRole.USER,
        content="hello",
    )

    assert message.message_id == "message_001"
    assert message.role == AiChatRole.USER
    assert message.content == "hello"


def test_ai_chat_session_contract_shape() -> None:
    session = AiChatSessionContract(session_id="session_001", user_id=None)

    assert session.session_id == "session_001"
    assert session.user_id is None


def test_ai_tool_request_contract_shape() -> None:
    request = AiToolRequestContract(
        request_id="tool_001",
        tool_name="market_data_status",
    )

    assert request.request_id == "tool_001"
    assert request.tool_name == "market_data_status"
    assert request.status == AiToolRequestStatus.DISABLED


def test_ai_chat_skeleton_status_locked() -> None:
    status = AiChatSkeletonStatus()

    assert status.stack == "ai_chat"
    assert status.phase == "phase_12_skeleton"
    assert status.ollama_adapter_implemented is False
    assert status.model_calls_enabled is False
    assert status.rag_implemented is False
    assert status.memory_implemented is False
    assert status.tool_use_implemented is False
    assert status.runtime_integration_implemented is False
    assert status.broker_integration_implemented is False
    assert status.trading_advice_implemented is False
    assert status.business_logic_implemented is False
EOF

cat > "$BACKEND/tests/smoke/test_ai_chat_status.py" <<'EOF'
from app.stacks.ai_chat.adapters.ollama_adapter import ollama_adapter_placeholder
from app.stacks.ai_chat.contracts.ai_chat_contract import (
    AiToolRequestContract,
    AiToolRequestStatus,
)
from app.stacks.ai_chat.services.ai_chat_service import (
    deny_all_ai_tool_requests_in_skeleton,
    get_ai_chat_skeleton_status,
)


def test_ai_chat_status_is_skeleton_only() -> None:
    status = get_ai_chat_skeleton_status()

    assert status.stack == "ai_chat"
    assert status.phase == "phase_12_skeleton"
    assert status.ollama_adapter_implemented is False
    assert status.model_calls_enabled is False
    assert status.rag_implemented is False
    assert status.memory_implemented is False
    assert status.tool_use_implemented is False
    assert status.runtime_integration_implemented is False
    assert status.broker_integration_implemented is False
    assert status.trading_advice_implemented is False
    assert status.business_logic_implemented is False


def test_ollama_placeholder_does_not_call_model() -> None:
    assert ollama_adapter_placeholder() == "phase_12_skeleton_only_no_model_calls"


def test_ai_tool_requests_are_denied() -> None:
    request = AiToolRequestContract(
        request_id="tool_001",
        tool_name="broker_status",
    )

    denied = deny_all_ai_tool_requests_in_skeleton(request)

    assert denied.status == AiToolRequestStatus.DENIED
EOF

cat > "$BACKEND/tests/architecture/test_ai_chat_phase_12_forbidden_terms.py" <<'EOF'
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STACK = ROOT / "app" / "stacks" / "ai_chat"

FORBIDDEN_TERMS = [
    "requests.post",
    "httpx.post",
    "ollama.chat",
    "ollama.generate",
    "model.generate",
    "execute_tool",
    "execute_trade",
    "submit_order",
    "place_order",
    "broker_client",
    "runtime_service",
    "financial_advice",
]


def test_ai_chat_phase_12_has_no_model_tool_or_execution_logic() -> None:
    scanned = []

    for path in STACK.rglob("*.py"):
        text = path.read_text(errors="ignore")
        scanned.append(path)

        for term in FORBIDDEN_TERMS:
            assert term not in text, f"Forbidden ai_chat implementation term {term!r} found in {path}"

    assert scanned
EOF

cat > "$ROOT/docs/contracts/PHASE_12_AI_CHAT_SKELETON_CONTRACT.md" <<'EOF'
# Phase 12 AI Chat Skeleton Contract

## Status

Phase 12 skeleton only.

## Purpose

Create the AI chat stack shape without implementing real model calls, RAG, memory, tool execution, runtime orchestration, broker interaction, trading advice, or business logic.

## Allowed

- chat message contract
- chat session contract
- AI tool request contract
- Ollama placeholder adapter
- skeleton denial service
- status service
- API placeholder
- tests
- certification artifact

## Forbidden

- real Ollama calls
- model inference
- RAG implementation
- memory implementation
- tool execution
- runtime execution
- broker interaction
- order placement
- trading advice implementation
- business logic

## Default State

- Ollama adapter implemented: false
- model calls enabled: false
- RAG implemented: false
- memory implemented: false
- tool use implemented: false
- runtime integration implemented: false
- broker integration implemented: false
- trading advice implemented: false

## Exit Criteria

- tests pass
- ai_chat stack has contracts/services/api/adapters placeholders
- all tool requests denied by skeleton
- no model calls exist
- no broker/runtime execution exists
EOF

cat > "$ROOT/certification/phase_01/PHASE_12_AI_CHAT_SKELETON_CERTIFICATION.md" <<'EOF'
# Phase 12 AI Chat Skeleton Certification

Status: pending

Checks:
- ai_chat contract exists
- skeleton service exists
- API placeholder exists
- Ollama placeholder exists
- all tool requests denied by default
- no real model calls
- no RAG implementation
- no memory implementation
- no runtime execution
- no broker implementation
- tests pass
EOF

echo
echo "Running Phase 12 tests..."
pytest

cat > "$ROOT/certification/phase_01/PHASE_12_AI_CHAT_SKELETON_CERTIFICATION.md" <<'EOF'
# Phase 12 AI Chat Skeleton Certification

Status: PASS

Checks:
- ai_chat contract exists
- skeleton service exists
- API placeholder exists
- Ollama placeholder exists
- all tool requests denied by default
- no real model calls
- no RAG implementation
- no memory implementation
- no runtime execution
- no broker implementation
- tests pass

Result:
- Phase 12 AI chat skeleton is certified.
EOF

echo
echo "========================================="
echo "PHASE 12 COMPLETE"
echo "========================================="
echo "PASS: AI Chat skeleton created and certified."
