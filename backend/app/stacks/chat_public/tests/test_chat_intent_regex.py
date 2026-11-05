from __future__ import annotations

import pytest

from backend.app.stacks.chat_public.chat_intent_regex import (
    ChatIntent,
    detect_chat_intent,
)


@pytest.mark.parametrize(
    ("message", "legacy_intent", "family", "subtype"),
    [
        (
            "hello",
            "general_conversation",
            "GENERAL",
            "greeting",
        ),
        (
            "Are you a happy wolf?",
            "general_conversation",
            "GENERAL",
            "personality",
        ),
        (
            "As your developer, how can I improve you?",
            "general_conversation",
            "DEVELOPER",
            "self_evaluation",
        ),
        (
            "Review the architecture.",
            "general_conversation",
            "DEVELOPER",
            "architecture_review",
        ),
        (
            "What capabilities are missing?",
            "general_conversation",
            "DEVELOPER",
            "self_evaluation",
        ),
        (
            "What should we build next?",
            "general_conversation",
            "DEVELOPER",
            "developer_review",
        ),
        (
            "What is the price of AAPL?",
            "trading_conversation",
            "MARKET",
            "market_analysis",
        ),
        (
            "Review my portfolio holdings.",
            "trading_conversation",
            "PORTFOLIO",
            "portfolio_review",
        ),
        (
            "graph reset",
            "graph_reset",
            "SYSTEM",
            "graph_reset",
        ),
        (
            "graph validate",
            "graph_validate",
            "SYSTEM",
            "graph_validate",
        ),
        (
            "simulate trade AAPL",
            "simulate_trade",
            "MARKET",
            "simulate_trade",
        ),
        (
            "Enable live trading and execute a real trade.",
            "blocked_live_execution",
            "SAFETY",
            "blocked_live_execution",
        ),
        (
            "Explain diversification.",
            "general_conversation",
            "GENERAL",
            "discussion",
        ),
    ],
)
def test_detect_chat_intent_v2_metadata_and_legacy_compatibility(
    message: str,
    legacy_intent: str,
    family: str,
    subtype: str,
) -> None:
    result = detect_chat_intent(message)

    assert result.intent == legacy_intent
    assert result.family == family
    assert result.subtype == subtype


def test_developer_pronoun_i_is_not_detected_as_ticker() -> None:
    result = detect_chat_intent(
        "As your developer, how can I improve you?"
    )

    assert result.symbol is None
    assert result.intent == "general_conversation"
    assert result.developer_mode is True
    assert result.self_evaluation is True


def test_market_symbol_is_preserved() -> None:
    result = detect_chat_intent(
        "What is the price of AAPL?"
    )

    assert result.symbol == "AAPL"
    assert result.intent == "trading_conversation"


def test_blocked_live_execution_remains_fail_closed() -> None:
    result = detect_chat_intent(
        "Enable live trading and execute a real trade."
    )

    assert result.blocked is True
    assert result.intent == "blocked_live_execution"


def test_chat_intent_legacy_constructor_remains_valid() -> None:
    result = ChatIntent(
        intent="general_conversation",
    )

    assert result.intent == "general_conversation"
    assert result.symbol is None
    assert result.blocked is False


def test_where_do_you_need_improvement_is_self_evaluation() -> None:
    result = detect_chat_intent(
        "where do you need improvement?"
    )

    assert result.self_evaluation is True
    assert result.subtype == "self_evaluation"


def test_explicit_strategy_creation_with_nonexecution_paper_trade_remains_trading() -> None:

    exact = detect_chat_intent(
        "Create a new RSI trading strategy for AAPL using an RSI entry, "
        "stop-loss, and take-profit. Present the strategy proposal for "
        "review only. Do not execute, paper trade, or send any order."
    )

    assert exact.intent == "trading_conversation"
    assert exact.family == "MARKET"

    direct = detect_chat_intent(
        "Create a new RSI trading strategy for AAPL. "
        "Do not paper trade."
    )

    assert direct.intent == "trading_conversation"
    assert direct.family == "MARKET"



def test_genuine_research_paper_requests_remain_research() -> None:

    research_paper = detect_chat_intent(
        "Find research papers about RSI trading strategies."
    )

    assert research_paper.intent == "research_conversation"
    assert research_paper.family == "RESEARCH"

    academic = detect_chat_intent(
        "Summarize an academic paper about momentum trading."
    )

    assert academic.intent == "research_conversation"
    assert academic.family == "RESEARCH"



def test_plain_paper_trading_question_preserves_existing_research_behavior() -> None:

    result = detect_chat_intent(
        "How does paper trading work?"
    )

    assert result.intent == "research_conversation"
    assert result.family == "RESEARCH"


def test_indicator_acronyms_do_not_preempt_actual_ticker() -> None:

    cases = (
        (
            "Create an RSI strategy for AAPL.",
            "AAPL",
        ),
        (
            "Create a MACD strategy for AAPL.",
            "AAPL",
        ),
        (
            "Create an SMA crossover strategy for MSFT.",
            "MSFT",
        ),
        (
            "Create an EMA crossover strategy for MSFT.",
            "MSFT",
        ),
        (
            "Create a trading strategy for AAPL using RSI.",
            "AAPL",
        ),
        (
            "For AAPL create a strategy using MACD.",
            "AAPL",
        ),
        (
            "For MSFT create a strategy using SMA crossover.",
            "MSFT",
        ),
    )

    for message, expected_symbol in cases:

        result = detect_chat_intent(
            message
        )

        assert result.intent == "trading_conversation"
        assert result.symbol == expected_symbol



def test_exact_strategy_candidate_positive_control_uses_aapl_symbol() -> None:

    result = detect_chat_intent(
        "Create a new RSI trading strategy for AAPL using an RSI entry, "
        "stop-loss, and take-profit. Present the strategy proposal for "
        "review only. Do not execute, paper trade, or send any order."
    )

    assert result.intent == "trading_conversation"
    assert result.family == "MARKET"
    assert result.symbol == "AAPL"



def test_plain_ticker_extraction_remains_intact() -> None:

    aapl = detect_chat_intent(
        "Analyze AAPL."
    )

    assert aapl.intent == "trading_conversation"
    assert aapl.symbol == "AAPL"

    msft = detect_chat_intent(
        "Analyze MSFT."
    )

    assert msft.intent == "trading_conversation"
    assert msft.symbol == "MSFT"



def test_indicator_only_terms_are_not_bound_as_stock_symbols() -> None:

    rsi = detect_chat_intent(
        "Explain RSI."
    )

    assert rsi.symbol is None

    macd = detect_chat_intent(
        "Explain MACD."
    )

    assert macd.symbol is None

    sma = detect_chat_intent(
        "Explain SMA."
    )

    assert sma.symbol is None

    ema = detect_chat_intent(
        "Explain EMA."
    )

    assert ema.symbol is None



def test_financial_acronym_etf_educational_guard_v1():
    from backend.app.stacks.chat_public.chat_intent_regex import (
        detect_chat_intent,
    )

    examples = [
        "Explain what an ETF is to a beginner.",
        "What is an ETF?",
        "How does an ETF work?",
    ]

    for question in examples:
        decision = detect_chat_intent(question)

        assert decision.symbol is None, (
            question,
            decision,
        )
        assert decision.subtype != "stock_lookup", (
            question,
            decision,
        )
