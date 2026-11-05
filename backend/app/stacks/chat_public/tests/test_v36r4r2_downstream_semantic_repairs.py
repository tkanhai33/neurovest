from __future__ import annotations

from backend.app.stacks.chat_public.chat_runtime import (
    _v36r4_downstream_semantic_repair,
)

from backend.app.stacks.chat_public.rag.strategy_library_truth import (
    build_strategy_library_truth_prompt,
)

from backend.app.stacks.chat_public.request_route_contract import (
    ChatAnswerRoute,
    classify_chat_route,
)


def test_v36r4r2_q24_final_empty_response_is_repaired():
    query = (
        "Can a diversified portfolio still have a high "
        "expected return? Explain without giving personalized advice."
    )

    answer = _v36r4_downstream_semantic_repair(
        query,
        "",
    )

    lowered = answer.lower()

    assert answer.strip()

    assert (
        "diversified portfolio can still have a high expected return"
        in lowered
    )

    assert "idiosyncratic" in lowered

    assert (
        "not personalized investment advice"
        in lowered
    )


def test_v36r4r2_q37_mixed_finance_gets_general_explanation_first():
    query = (
        "Explain mean reversion as a general finance concept, "
        "then distinguish it from NeuroVest strategy "
        "SSRN_3247865_067."
    )

    strategy_only = (
        "SSRN_3247865_067 | Mean-reversion "
        "Approved local research source: "
        "[chunk_example]"
    )

    answer = _v36r4_downstream_semantic_repair(
        query,
        strategy_only,
    )

    lowered = answer.lower()

    assert answer.startswith(
        "Mean reversion is the general finance idea"
    )

    assert "historical average" in lowered

    assert "ssrn_3247865_067" in lowered

    assert "mean-reversion" in lowered


def test_v36r4r2_q37_strategy_truth_prompt_marks_identity_supplemental():
    query = (
        "Explain mean reversion as a general finance concept, "
        "then distinguish it from NeuroVest strategy "
        "SSRN_3247865_067."
    )

    prompt = build_strategy_library_truth_prompt(
        query
    )

    assert "MIXED-DOMAIN REQUEST CONTRACT" in prompt

    assert (
        "MUST NOT replace the user's separate finance or developer question"
        in prompt
    )

    assert "SSRN_3247865_067" in prompt


def test_v36r4r2_pure_strategy_identity_still_has_authoritative_contract():
    query = "What is SSRN_3247865_067?"

    prompt = build_strategy_library_truth_prompt(
        query
    )

    assert (
        "REQUEST-SPECIFIC AUTHORITATIVE REQUIREMENT"
        in prompt
    )

    assert "SSRN_3247865_067" in prompt

    assert (
        "MIXED-DOMAIN REQUEST CONTRACT"
        not in prompt
    )


def test_v36r4r2_q40_async_substance_is_enforced():
    query = (
        "If I ask about Python async code and also mention "
        "SSRN_3247865_053, should the answer become a "
        "strategy-library dump? Explain the coding issue while "
        "keeping the strategy reference separate."
    )

    weak_answer = (
        "No, I will keep the coding explanation separate. "
        "SSRN_3247865_053 | Price-momentum."
    )

    answer = _v36r4_downstream_semantic_repair(
        query,
        weak_answer,
    )

    lowered = answer.lower()

    assert "`async def` defines a coroutine function" in answer

    assert "await" in lowered

    assert "event loop" in lowered

    assert "ssrn_3247865_053" in lowered

    assert "price-momentum" in lowered


def test_v36r4r2_routes_remain_unchanged():
    q24 = classify_chat_route(
        (
            "Can a diversified portfolio still have a high "
            "expected return? Explain without giving personalized advice."
        )
    )

    q37 = classify_chat_route(
        (
            "Explain mean reversion as a general finance concept, "
            "then distinguish it from NeuroVest strategy "
            "SSRN_3247865_067."
        )
    )

    q40 = classify_chat_route(
        (
            "If I ask about Python async code and also mention "
            "SSRN_3247865_053, should the answer become a "
            "strategy-library dump? Explain the coding issue while "
            "keeping the strategy reference separate."
        )
    )

    assert q24.route == ChatAnswerRoute.GENERAL_FINANCE
    assert q37.route == ChatAnswerRoute.GENERAL_FINANCE
    assert q40.route == ChatAnswerRoute.DEVELOPER_REPOSITORY

    assert q24.deterministic_answer is False
    assert q37.deterministic_answer is False
    assert q40.deterministic_answer is False
