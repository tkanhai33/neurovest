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
