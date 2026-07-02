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
