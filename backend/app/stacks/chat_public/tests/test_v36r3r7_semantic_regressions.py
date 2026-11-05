from __future__ import annotations

import json

from backend.app.stacks.chat_public.chat_intent_regex import (
    detect_chat_intent,
)
from backend.app.stacks.chat_public.chat_runtime import (
    _v36r3_finance_semantic_guard,
)
from backend.app.stacks.chat_public.deterministic_answers import (
    deterministic_strategy_answer,
)
from backend.app.stacks.chat_public.math_tools.live_math import (
    extract_math_request,
    evaluate_live_math,
)
from backend.app.stacks.chat_public.request_route_contract import (
    ChatAnswerRoute,
    classify_chat_route,
)


def test_legacy_plain_diversification_intent_is_unchanged():
    result = detect_chat_intent(
        "Explain diversification."
    )

    assert result.intent == "general_conversation"
    assert result.family == "GENERAL"
    assert result.subtype == "discussion"


def test_q02_price_momentum_name_resolves_to_053():
    query = (
        "What is the NeuroVest strategy named "
        "Price-momentum and what is its SSRN ID?"
    )

    contract = classify_chat_route(
        query
    )

    assert (
        contract.route
        == ChatAnswerRoute.STRATEGY_LIBRARY_IDENTITY
    )

    answer = deterministic_strategy_answer(
        query,
        contract,
    )

    assert answer is not None
    assert "Price-momentum" in answer
    assert "SSRN_3247865_053" in answer


def test_q04_unknown_strategy_id_still_fails_closed():
    query = "What is SSRN_3247865_999?"

    contract = classify_chat_route(
        query
    )

    answer = deterministic_strategy_answer(
        query,
        contract,
    )

    assert answer is not None
    assert "SSRN_3247865_999" in answer
    assert "not present" in answer.lower()


def test_q22_expected_return_diversification_routes_finance():
    query = (
        "Does diversification inherently mean lower "
        "expected returns?"
    )

    intent = detect_chat_intent(
        query
    )

    assert intent.intent == "trading_conversation"
    assert intent.family == "MARKET"
    assert intent.subtype == "general_finance_reasoning"

    answer = _v36r3_finance_semantic_guard(
        query,
        "Diversification always means lower expected returns.",
    )

    assert (
        "does not inherently mean lower expected returns"
        in answer.lower()
    )


def test_q24_diversified_high_expected_return():
    query = (
        "Can a diversified portfolio still have a high "
        "expected return?"
    )

    answer = _v36r3_finance_semantic_guard(
        query,
        "",
    )

    assert (
        "diversified portfolio can still have a high expected return"
        in answer.lower()
    )


def test_q35_percentage_adjustment_returns_270():
    query = (
        "A $250 amount increases by 8%. "
        "What is the new amount?"
    )

    extracted = extract_math_request(
        query
    )

    assert extracted is not None
    assert extracted.request.operation == "arithmetic"

    bundle = evaluate_live_math(
        query,
        requested=True,
    )

    assert bundle.extracted
    assert bundle.succeeded
    assert bundle.grounded

    serialized = json.dumps(
        bundle.result,
        sort_keys=True,
    )

    assert "270.00" in serialized


def test_q35_decrease_control_returns_230():
    query = (
        "A $250 amount decreases by 8%. "
        "What is the new amount?"
    )

    bundle = evaluate_live_math(
        query,
        requested=True,
    )

    assert bundle.extracted
    assert bundle.succeeded
    assert bundle.grounded

    serialized = json.dumps(
        bundle.result,
        sort_keys=True,
    )

    assert "230.00" in serialized


def test_q37_mixed_finance_strategy_not_identity_only():
    query = (
        "Explain mean reversion as a general finance concept, "
        "then distinguish it from NeuroVest strategy "
        "SSRN_3247865_067."
    )

    contract = classify_chat_route(
        query
    )

    assert (
        contract.route
        == ChatAnswerRoute.GENERAL_FINANCE
    )

    assert contract.deterministic_answer is False

    assert (
        deterministic_strategy_answer(
            query,
            contract,
        )
        is None
    )


def test_q40_mixed_async_strategy_routes_developer():
    query = (
        "If I ask about Python async code and also mention "
        "SSRN_3247865_053, should the answer become a "
        "strategy-library dump? Explain the coding issue while "
        "keeping the strategy reference separate."
    )

    contract = classify_chat_route(
        query
    )

    assert (
        contract.route
        == ChatAnswerRoute.DEVELOPER_REPOSITORY
    )

    assert contract.deterministic_answer is False

    intent = detect_chat_intent(
        query
    )

    assert intent.family == "DEVELOPER"

    assert (
        intent.subtype
        == "mixed_developer_strategy"
    )
