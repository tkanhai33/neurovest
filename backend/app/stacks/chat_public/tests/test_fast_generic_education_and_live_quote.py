from __future__ import annotations

from datetime import UTC, datetime
from backend.app.stacks.market_data.dto import MarketQuote
from types import SimpleNamespace

from backend.app.stacks.chat_public import chat_runtime
from backend.app.stacks.chat_public.cognitive_model_router import (
    NEURO_FAST_MODEL,
    NEURO_REASON_MODEL,
    route_cognitive_request,
)


class GenericPortfolioIntent:
    intent = "trading_conversation"
    family = "PORTFOLIO"
    subtype = "portfolio_review"
    developer_mode = False
    requires_repo_context = False
    requires_architecture_context = False


def test_generic_portfolio_education_uses_fast_model() -> None:
    decision = route_cognitive_request(
        "How does concentration in one industry affect a portfolio?",
        intent=GenericPortfolioIntent(),
    )

    assert decision.model == NEURO_FAST_MODEL


def test_personal_portfolio_question_keeps_reason_model() -> None:
    decision = route_cognitive_request(
        "What are the concentration risks in my portfolio?",
        intent=GenericPortfolioIntent(),
    )

    assert decision.model == NEURO_REASON_MODEL


def test_current_quote_uses_read_only_market_runtime(
    monkeypatch,
) -> None:
    quote = MarketQuote(
        symbol="NVDA",
        price=225.51,
        currency="USD",
        previous_close=228.87,
        observed_at=datetime.now(UTC),
        provider="yfinance",
        delayed=False,
    )

    runtime = SimpleNamespace(
        router=SimpleNamespace(
            get_quote=lambda symbol, use_cache: quote,
        )
    )

    monkeypatch.setattr(
        chat_runtime,
        "get_market_data_runtime",
        lambda: runtime,
    )

    intent = SimpleNamespace(
        blocked=False,
        intent="trading_conversation",
        symbol="NVDA",
    )

    result = chat_runtime.handle_chat_message(
        "What is the current price of NVDA?",
        detected_intent=intent,
    )

    assert result["status"] == "ok"
    assert result["provider"] == "yfinance"
    assert result["model"] is None
    assert result["tool_truth_state"] == "grounded"
    assert "225.51 USD" in result["response"]["message"]
    assert "no order was created" in result["response"]["message"]
