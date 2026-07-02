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
