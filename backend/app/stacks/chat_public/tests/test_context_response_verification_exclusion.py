from __future__ import annotations

from backend.app.stacks.chat_public.context.context_assembler import (
    _is_model_relevant_tool_evidence,
)


class Evidence:
    def __init__(self, tool_name: str) -> None:
        self.tool_name = tool_name


def test_response_verification_is_not_model_context() -> None:
    assert not _is_model_relevant_tool_evidence(
        Evidence("response_verification")
    )

    assert not _is_model_relevant_tool_evidence(
        {"tool_name": "RESPONSE_VERIFICATION"}
    )


def test_historical_retrieval_is_not_model_context() -> None:
    assert not _is_model_relevant_tool_evidence(
        Evidence("local_knowledge_retrieval")
    )

    assert not _is_model_relevant_tool_evidence(
        {"tool_name": "LOCAL_KNOWLEDGE_RETRIEVAL"}
    )


def test_real_tool_evidence_remains_available_to_model() -> None:
    assert _is_model_relevant_tool_evidence(
        Evidence("market_data_lookup")
    )

    assert _is_model_relevant_tool_evidence(
        {"tool_name": "deterministic_math"}
    )
