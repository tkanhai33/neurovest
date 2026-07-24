from __future__ import annotations

from types import SimpleNamespace

import pytest

from backend.app.stacks.chat_public.cognitive_model_router import (
    NEURO_CODE_MODEL,
    NEURO_FALLBACK_MODEL,
    NEURO_FAST_MODEL,
    NEURO_REASON_MODEL,
    CognitiveRoutingDecision,
    route_cognitive_request,
)


def intent(
    *,
    intent_name: str = "general_conversation",
    family: str = "GENERAL",
    subtype: str = "discussion",
    developer_mode: bool = False,
    requires_repo_context: bool = False,
    requires_architecture_context: bool = False,
):
    return SimpleNamespace(
        intent=intent_name,
        family=family,
        subtype=subtype,
        developer_mode=developer_mode,
        requires_repo_context=requires_repo_context,
        requires_architecture_context=(
            requires_architecture_context
        ),
    )


def test_routing_decision_is_immutable() -> None:
    decision = route_cognitive_request(
        "Hello",
        intent=intent(),
    )

    with pytest.raises(
        AttributeError,
    ):
        decision.model = "changed"  # type: ignore[misc]


def test_general_greeting_uses_fast_model() -> None:
    decision = route_cognitive_request(
        "Hello",
        intent=intent(
            subtype="greeting",
        ),
    )

    assert decision.tier == "fast"
    assert decision.model == NEURO_FAST_MODEL
    assert decision.fallback_model == NEURO_FALLBACK_MODEL
    assert decision.deterministic_tool_required is False
    assert decision.retrieval_required is False


@pytest.mark.parametrize(
    "message",
    [
        "Analyze the risk in my portfolio.",
        "Create a paper-trading momentum strategy.",
        "Compare value and growth strategies.",
        "Why did this stock strategy underperform?",
    ],
)
def test_analysis_and_strategy_use_reason_model(
    message: str,
) -> None:
    decision = route_cognitive_request(
        message,
        intent=intent(
            intent_name="trading_conversation",
            family="MARKET",
            subtype="market_analysis",
        ),
    )

    assert decision.tier == "reason"
    assert decision.model == NEURO_REASON_MODEL


@pytest.mark.parametrize(
    "message",
    [
        "Write a FastAPI endpoint.",
        "Debug this Python traceback.",
        "Review the NeuroVest repository architecture.",
        "Why is this pytest failing?",
    ],
)
def test_code_work_uses_code_model(
    message: str,
) -> None:
    decision = route_cognitive_request(
        message,
        intent=intent(
            family="DEVELOPER",
            developer_mode=True,
            requires_repo_context=True,
        ),
    )

    assert decision.tier == "code"
    assert decision.model == NEURO_CODE_MODEL
    assert decision.retrieval_required is True


@pytest.mark.parametrize(
    "message",
    [
        "Calculate a 17.5 percent return on 2400.",
        "What is the drawdown from 120 to 87?",
        "Compute the cost basis of 12 shares at 42.75.",
        "Solve 1250 * 0.08.",
    ],
)
def test_math_declares_deterministic_tool_requirement(
    message: str,
) -> None:
    decision = route_cognitive_request(
        message,
        intent=intent(),
    )

    assert decision.tier == "reason"
    assert decision.model == NEURO_REASON_MODEL
    assert decision.deterministic_tool_required is True


@pytest.mark.parametrize(
    "message",
    [
        "What is AAPL trading at today?",
        "Review my portfolio positions.",
        "What does the NeuroVest architecture say?",
        "Give me the latest market news.",
    ],
)
def test_current_or_account_data_declares_retrieval(
    message: str,
) -> None:
    decision = route_cognitive_request(
        message,
        intent=intent(),
    )

    assert decision.retrieval_required is True
    assert decision.tier in {
        "reason",
        "code",
    }


def test_decision_serializes_complete_contract() -> None:
    decision = route_cognitive_request(
        "Analyze my portfolio return.",
        intent=intent(
            intent_name="trading_conversation",
            family="PORTFOLIO",
            subtype="portfolio_review",
        ),
    )

    payload = decision.as_dict()

    assert set(payload) == {
        "tier",
        "model",
        "reason",
        "intent",
        "family",
        "subtype",
        "deterministic_tool_required",
        "retrieval_required",
        "fallback_model",
    }

    assert isinstance(
        decision,
        CognitiveRoutingDecision,
    )




def test_exact_authenticated_math_prompt_requires_deterministic_tool() -> None:
    decision = route_cognitive_request(
        "What is 17.5 percent of 2480?",
        intent=intent(),
    )

    assert decision.tier == "reason"
    assert decision.model == NEURO_REASON_MODEL
    assert decision.deterministic_tool_required is True
    assert decision.retrieval_required is False


def test_exact_authenticated_research_prompt_requires_retrieval() -> None:
    decision = route_cognitive_request(
        (
            "Using the local research library, "
            "explain the Fama French three factor model "
            "and include the approved source citations."
        ),
        intent=intent(),
    )

    assert decision.tier == "reason"
    assert decision.model == NEURO_REASON_MODEL
    assert decision.deterministic_tool_required is False
    assert decision.retrieval_required is True


@pytest.mark.parametrize(
    "message",
    [
        "What is 10 percent of 500?",
        "What is 17.5 percent of 2480?",
        "Compute 12 percent of 900.",
        "Calculate 1250 * 0.08.",
    ],
)
def test_common_math_phrasing_requires_deterministic_tool(
    message: str,
) -> None:
    decision = route_cognitive_request(
        message,
        intent=intent(),
    )

    assert decision.deterministic_tool_required is True


@pytest.mark.parametrize(
    "message",
    [
        "Use the local research library.",
        "Explain this using academic research.",
        "Include the approved source citations.",
        "Use the SSRN research papers.",
        "Explain the Fama French model from the research library.",
    ],
)
def test_local_research_phrasing_requires_retrieval(
    message: str,
) -> None:
    decision = route_cognitive_request(
        message,
        intent=intent(),
    )

    assert decision.retrieval_required is True









def test_position_size_uses_math_without_retrieval() -> None:
    decision = route_cognitive_request(
        (
            "Calculate position size with account value 25000, "
            "risk 1 percent, entry 52.50, and stop 50.00."
        ),
        intent=intent(
            intent_name="trading_conversation",
            family="PORTFOLIO",
            subtype="portfolio_review",
        ),
    )

    assert decision.tier == "reason"
    assert decision.deterministic_tool_required is True
    assert decision.retrieval_required is False


@pytest.mark.parametrize(
    "message",
    [
        (
            "For this conversation only, remember that the "
            "sample portfolio project codename is Aurora. "
            "Reply briefly."
        ),
        (
            "What is the sample portfolio project codename "
            "I gave you earlier?"
        ),
    ],
)
def test_conversation_memory_avoids_retrieval(
    message: str,
) -> None:
    decision = route_cognitive_request(
        message,
        intent=intent(
            intent_name="trading_conversation",
            family="PORTFOLIO",
            subtype="portfolio_review",
        ),
    )

    assert decision.deterministic_tool_required is False
    assert decision.retrieval_required is False


@pytest.mark.parametrize(
    "message",
    [
        "What is the current price of AAPL?",
        "Review my portfolio holdings.",
        "Show my positions.",
        "Use the local research library.",
        "Include approved source citations.",
    ],
)
def test_explicit_retrieval_requests_remain_enabled(
    message: str,
) -> None:
    decision = route_cognitive_request(
        message,
        intent=intent(
            intent_name="trading_conversation",
            family="PORTFOLIO",
            subtype="portfolio_review",
        ),
    )

    assert decision.retrieval_required is True




def test_strategy_family_retains_retrieval_contract() -> None:
    decision = route_cognitive_request(
        "Develop and evaluate a portfolio strategy.",
        intent=intent(
            intent_name="trading_conversation",
            family="STRATEGY",
            subtype="discussion",
        ),
    )

    assert decision.tier == "reason"
    assert decision.deterministic_tool_required is False
    assert decision.retrieval_required is True


@pytest.mark.parametrize(
    (
        "message",
        "family",
        "expected_math",
    ),
    [
        (
            (
                "Calculate position size with account value 25000, "
                "risk 1 percent, entry 52.50, and stop 50.00."
            ),
            "PORTFOLIO",
            True,
        ),
        (
            (
                "For this conversation only, remember that the "
                "sample portfolio project codename is Aurora."
            ),
            "PORTFOLIO",
            False,
        ),
        (
            (
                "What is the sample portfolio project codename "
                "I gave you earlier?"
            ),
            "PORTFOLIO",
            False,
        ),
        (
            "Explain basic market diversification.",
            "MARKET",
            False,
        ),
    ],
)
def test_market_and_portfolio_family_do_not_force_retrieval(
    message: str,
    family: str,
    expected_math: bool,
) -> None:
    decision = route_cognitive_request(
        message,
        intent=intent(
            intent_name="trading_conversation",
            family=family,
            subtype="discussion",
        ),
    )

    assert (
        decision.deterministic_tool_required
        is expected_math
    )

    assert decision.retrieval_required is False


def test_router_never_exposes_execution_authority() -> None:
    payload = route_cognitive_request(
        "Build a strategy.",
        intent=intent(
            family="STRATEGY",
        ),
    ).as_dict()

    forbidden = {
        "broker_execution_enabled",
        "live_trading_enabled",
        "place_order",
        "execute_trade",
        "user_id",
        "account_id",
    }

    assert forbidden.isdisjoint(
        payload
    )
