from __future__ import annotations

import pytest

from backend.app.stacks.chat_public.chat_runtime import (
    _v36r4_normalize_response_tool_truth_state,
)

from backend.app.stacks.chat_public.contracts.chat_contracts import (
    ChatResponse,
)


@pytest.mark.parametrize(
    "state",
    [
        "grounded",
        "partial",
        "ungrounded",
        "not_required",
    ],
)
def test_valid_tool_truth_state_is_preserved(
    state: str,
) -> None:

    result = _v36r4_normalize_response_tool_truth_state(
        state,
        retrieval_requested=False,
        retrieval_grounded=False,
        math_requested=False,
        math_grounded=False,
    )

    assert result == state


def test_deterministic_tool_required_without_actual_tool_request_maps_not_required():
    result = _v36r4_normalize_response_tool_truth_state(
        "deterministic_tool_required",
        retrieval_requested=False,
        retrieval_grounded=False,
        math_requested=False,
        math_grounded=False,
    )

    assert result == "not_required"


def test_invalid_internal_state_with_grounded_math_maps_grounded():
    result = _v36r4_normalize_response_tool_truth_state(
        "deterministic_tool_required",
        retrieval_requested=False,
        retrieval_grounded=False,
        math_requested=True,
        math_grounded=True,
    )

    assert result == "grounded"


def test_invalid_internal_state_with_failed_requested_math_maps_ungrounded():
    result = _v36r4_normalize_response_tool_truth_state(
        "deterministic_tool_required",
        retrieval_requested=False,
        retrieval_grounded=False,
        math_requested=True,
        math_grounded=False,
    )

    assert result == "ungrounded"


def test_invalid_internal_state_with_grounded_retrieval_maps_grounded():
    result = _v36r4_normalize_response_tool_truth_state(
        "deterministic_tool_required",
        retrieval_requested=True,
        retrieval_grounded=True,
        math_requested=False,
        math_grounded=False,
    )

    assert result == "grounded"


def test_normalized_value_is_accepted_by_chat_response_contract():
    state = _v36r4_normalize_response_tool_truth_state(
        "deterministic_tool_required",
        retrieval_requested=False,
        retrieval_grounded=False,
        math_requested=False,
        math_grounded=False,
    )

    response = ChatResponse(
        status="ok",
        thread_id="test-thread",
        user_message_id="test-user-message",
        assistant_message_id=None,
        message="test",
        intent="trading_conversation",
        provider="test",
        model="test",
        tool_truth_state=state,
    )

    assert response.tool_truth_state == "not_required"
