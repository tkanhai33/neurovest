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
