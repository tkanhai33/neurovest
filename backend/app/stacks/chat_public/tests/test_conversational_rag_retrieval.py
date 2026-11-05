from __future__ import annotations

from backend.app.stacks.chat_public.cognitive_model_router import (
    route_cognitive_request,
)
from backend.app.stacks.chat_public.rag.contracts import (
    RetrievalResult,
)
from backend.app.stacks.chat_public.rag.live_retrieval import (
    LIVE_RAG_MAX_RESULTS_PER_SOURCE,
    retrieve_live_evidence,
)


class GeneralIntent:
    intent = "general_conversation"
    family = "GENERAL"
    subtype = "discussion"
    developer_mode = False
    requires_repo_context = False
    requires_architecture_context = False


class FakeIndex:
    def __init__(self, results):
        self.results = list(results)

    def retrieve(self, query, *, top_k, minimum_score):
        return self.results[:top_k]


def _result(number, source_path):
    return RetrievalResult(
        chunk_id=f"chunk-{number}",
        document_id=f"document-{number}",
        source_path=source_path,
        title=f"Source {number}",
        text="Educational investment research evidence.",
        score=0.99 - number / 100,
        citation=f"[chunk-{number}]",
        metadata={
            "page_number": number,
            "prompt_injection_detected": False,
            "research_corpus": True,
        },
    )


def test_investor_education_topics_activate_retrieval() -> None:
    decision = route_cognitive_request(
        "Explain diversification and concentration risk.",
        intent=GeneralIntent(),
    )

    assert decision.retrieval_required is True


def test_retrieval_limits_one_source_to_two_results() -> None:
    bundle = retrieve_live_evidence(
        "Explain diversification.",
        requested=True,
        index=FakeIndex(
            [
                _result(1, "knowledge/research/ssrn/large-paper.pdf"),
                _result(2, "knowledge/research/ssrn/large-paper.pdf"),
                _result(3, "knowledge/research/ssrn/large-paper.pdf"),
                _result(4, "knowledge/research/guides/diversification.md"),
                _result(5, "knowledge/research/guides/strategy.md"),
                _result(6, "knowledge/research/academic/factors.pdf"),
            ]
        ),
    )

    source_counts = {}

    for item in bundle.results:
        source_counts[item.source_path] = (
            source_counts.get(item.source_path, 0) + 1
        )

    assert len(bundle.results) == 5
    assert max(source_counts.values()) == (
        LIVE_RAG_MAX_RESULTS_PER_SOURCE
    )
    assert (
        "knowledge/research/guides/diversification.md"
        in source_counts
    )
