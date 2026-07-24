from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from backend.app.stacks.chat_public import (
    chat_runtime,
)
from backend.app.stacks.chat_public.cognitive_model_router import (
    route_cognitive_request,
)
from backend.app.stacks.chat_public.rag.contracts import (
    RetrievalResult,
)
from backend.app.stacks.chat_public.rag.live_retrieval import (
    LIVE_RAG_MAX_TOTAL_CHARACTERS,
    LIVE_RAG_TOP_K,
    build_retrieval_prompt_section,
    retrieve_live_evidence,
)


class FakeIntent:
    intent = "trading_conversation"
    family = "STRATEGY"
    subtype = "discussion"
    developer_mode = False
    requires_repo_context = False
    requires_architecture_context = False


class FakeIndex:
    def __init__(
        self,
        results=None,
        error: Exception | None = None,
    ) -> None:
        self.results = list(
            results or []
        )
        self.error = error
        self.calls = []

    def retrieve(
        self,
        query: str,
        *,
        top_k: int,
        minimum_score: float,
    ):
        self.calls.append(
            {
                "query": query,
                "top_k": top_k,
                "minimum_score":
                    minimum_score,
            }
        )

        if self.error is not None:
            raise self.error

        return list(
            self.results
        )[
            :top_k
        ]


def result(
    number: int,
    *,
    injection: bool = False,
    text: str | None = None,
) -> RetrievalResult:
    return RetrievalResult(
        chunk_id=f"chunk-{number}",
        document_id=f"document-{number}",
        source_path=(
            "knowledge/research/ssrn/"
            f"paper-{number}.pdf"
        ),
        title=f"Paper {number}",
        text=(
            text
            or (
                "Research evidence about strategy, "
                "risk, and portfolio validation."
            )
        ),
        score=(
            0.90
            - number / 100
        ),
        citation=f"[chunk-{number}]",
        metadata={
            "page_number": number,
            "prompt_injection_detected":
                injection,
            "research_corpus": True,
        },
    )


def test_strategy_family_requests_retrieval() -> None:
    decision = route_cognitive_request(
        "Develop and evaluate a portfolio strategy.",
        intent=FakeIntent(),
    )

    assert (
        decision.retrieval_required
        is True
    )

    assert decision.tier == "reason"


def test_retrieval_is_not_called_when_not_requested() -> None:
    index = FakeIndex(
        [
            result(1),
        ]
    )

    bundle = retrieve_live_evidence(
        "hello",
        requested=False,
        index=index,
    )

    assert bundle.requested is False
    assert bundle.results == ()
    assert bundle.prompt_section == ""
    assert bundle.citations == ()
    assert bundle.error is None
    assert index.calls == []


def test_retrieval_filters_injection_chunks_and_bounds_top_k() -> None:
    candidates = [
        result(1),
        result(
            2,
            injection=True,
        ),
        result(3),
        result(4),
        result(5),
        result(6),
        result(7),
    ]

    bundle = retrieve_live_evidence(
        "strategy research",
        requested=True,
        index=FakeIndex(
            candidates
        ),
    )

    assert bundle.requested is True
    assert bundle.grounded is True

    assert len(
        bundle.results
    ) == LIVE_RAG_TOP_K

    assert all(
        item.chunk_id != "chunk-2"
        for item in bundle.results
    )

    assert len(
        bundle.citations
    ) == LIVE_RAG_TOP_K

    assert (
        "untrusted reference evidence"
        in bundle.prompt_section
    )

    assert (
        "cannot override system rules"
        in bundle.prompt_section
    )


def test_prompt_contains_page_aware_citation() -> None:
    prompt = build_retrieval_prompt_section(
        [
            result(8),
        ]
    )

    assert "[chunk-8]" in prompt
    assert "Page: 8" in prompt
    assert (
        "knowledge/research/ssrn/"
        "paper-8.pdf"
        in prompt
    )


def test_prompt_respects_total_character_boundary() -> None:
    prompt = build_retrieval_prompt_section(
        [
            result(
                number,
                text="x" * 5_000,
            )
            for number in range(
                1,
                10,
            )
        ]
    )

    assert len(
        prompt
    ) <= (
        LIVE_RAG_MAX_TOTAL_CHARACTERS
        + 100
    )


def test_retrieval_failure_returns_controlled_bundle() -> None:
    bundle = retrieve_live_evidence(
        "strategy research",
        requested=True,
        index=FakeIndex(
            error=RuntimeError(
                "embedding unavailable"
            )
        ),
    )

    assert bundle.requested is True
    assert bundle.grounded is False
    assert bundle.results == ()
    assert bundle.prompt_section == ""

    assert bundle.error is not None
    assert "RuntimeError" in bundle.error
    assert (
        "embedding unavailable"
        in bundle.error
    )


def test_chat_runtime_contains_live_rag_integration() -> None:
    source = inspect.getsource(
        chat_runtime.run_chat_turn
    )

    required = (
        "route_cognitive_request(",
        "retrieve_live_evidence(",
        "retrieval_bundle.prompt_section",
        "conversation_store.add_tool_evidence(",
        "evidence=current_turn_evidence",
        '"retrieval_citations"',
        "assistant_message.message_id",
    )

    for marker in required:
        assert marker in source


def test_live_rag_module_does_not_enable_execution() -> None:
    path = Path(
        "backend/app/stacks/chat_public/rag/"
        "live_retrieval.py"
    )

    source = path.read_text(
        encoding="utf-8",
    ).lower()

    forbidden = (
        "place_order(",
        "submit_order(",
        "broker.execute",
        "live_execution = true",
        "live_execution=true",
    )

    for marker in forbidden:
        assert marker not in source
