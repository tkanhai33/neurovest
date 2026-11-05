
"""General programming education must not imply repository access."""

import pytest

from backend.app.stacks.chat_public.request_route_contract import (
    ChatAnswerRoute,
    classify_chat_route,
)


@pytest.mark.parametrize(
    "message",
    [
        "Explain this Python async function.",
        "Explain Python decorators.",
        "What is a JavaScript promise?",
        "How does SQL indexing work?",
        "Teach me TypeScript generics.",
    ],
)
def test_general_coding_has_no_repository_context(message):
    decision = classify_chat_route(message)

    assert decision.route == ChatAnswerRoute.GENERAL_CHAT
    assert decision.repository_context_allowed is False
    assert decision.retrieval_allowed is False
    assert decision.developer_model_preferred is True


@pytest.mark.parametrize(
    "message",
    [
        "Explain NeuroVest's Python chat runtime.",
        "Inspect the repository Python code.",
        "Explain our backend Python implementation.",
    ],
)
def test_repository_specific_requests_keep_governed_routing(message):
    decision = classify_chat_route(message)

    assert decision.route == ChatAnswerRoute.DEVELOPER_REPOSITORY
    assert decision.repository_context_allowed is True


def test_financial_research_path_preserved():
    decision = classify_chat_route(
        "Compare academic research on momentum investing."
    )
    assert decision.route == ChatAnswerRoute.GENERAL_FINANCE
    assert decision.repository_context_allowed is False
