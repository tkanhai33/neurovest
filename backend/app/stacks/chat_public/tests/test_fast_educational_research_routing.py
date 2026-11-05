from __future__ import annotations

from backend.app.stacks.chat_public.cognitive_model_router import (
    NEURO_FAST_MODEL,
    NEURO_REASON_MODEL,
    route_cognitive_request,
)


class GeneralIntent:
    intent = "general_conversation"
    family = "GENERAL"
    subtype = "discussion"
    developer_mode = False
    requires_repo_context = False
    requires_architecture_context = False


class PortfolioIntent:
    intent = "trading_conversation"
    family = "PORTFOLIO"
    subtype = "portfolio_review"
    developer_mode = False
    requires_repo_context = False
    requires_architecture_context = False


def test_educational_research_uses_fast_grounded_route() -> None:
    decision = route_cognitive_request(
        "Explain the Fama-French three-factor model.",
        intent=GeneralIntent(),
    )

    assert decision.tier == "fast"
    assert decision.model == NEURO_FAST_MODEL
    assert decision.retrieval_required is True


def test_portfolio_reasoning_keeps_reason_model() -> None:
    decision = route_cognitive_request(
        "Evaluate my portfolio concentration risk.",
        intent=PortfolioIntent(),
    )

    assert decision.tier == "reason"
    assert decision.model == NEURO_REASON_MODEL
