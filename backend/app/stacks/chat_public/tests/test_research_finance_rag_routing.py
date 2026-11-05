from __future__ import annotations

import pytest

from backend.app.stacks.chat_public.request_route_contract import (
    ChatAnswerRoute,
    classify_chat_route,
)


@pytest.mark.parametrize(
    "query",
    (
        "Explain the Fama-French three-factor model.",
        "Why does diversification reduce company-specific risk?",
        "What are the risks of momentum investing?",
        "How should I approach strategy evaluation and backtesting?",
    ),
)
def test_research_finance_questions_allow_local_rag(query) -> None:
    contract = classify_chat_route(query)

    assert contract.route == ChatAnswerRoute.GENERAL_FINANCE
    assert contract.retrieval_allowed is True
    assert contract.strategy_truth_allowed is False
    assert contract.finance_model_preferred is True
