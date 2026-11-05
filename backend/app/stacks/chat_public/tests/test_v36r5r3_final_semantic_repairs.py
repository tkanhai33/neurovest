from __future__ import annotations

from backend.app.stacks.chat_public.chat_runtime import (
    _v36r5_final_answer_quality_repair,
)


def repair(
    query: str,
    response: str = "bad placeholder",
) -> str:

    return _v36r5_final_answer_quality_repair(
        query,
        response,
    )


def test_q12_imports_asyncio():

    answer = repair(
        "Show a small FastAPI endpoint that awaits an "
        "async database helper correctly."
    )

    assert "import asyncio" in answer
    assert "asyncio.sleep" in answer
    assert "await fetch_users_from_db()" in answer


def test_q13_correct_coroutine_semantics():

    answer = repair(
        "Explain the difference between await some_async_function() "
        "and calling some_async_function() without await."
    )

    lowered = answer.lower()

    assert "coroutine object" in lowered
    assert "does not automatically make it run" in lowered
    assert "event loop" in lowered
    assert "does not mean blocking" in lowered


def test_q18_logout_current_vs_all_sessions():

    answer = repair(
        "What is the difference between NeuroVest /auth/logout "
        "and /auth/logout-all?"
    )

    lowered = answer.lower()

    assert "current authenticated session" in lowered
    assert "all active sessions" in lowered
    assert "current session versus all sessions" in lowered


def test_q21_diversification_does_not_require_lower_expected_return():

    answer = repair(
        "Explain the main risk trade-offs between a concentrated "
        "portfolio and a diversified portfolio. Do not give "
        "personalized investment advice."
    )

    lowered = answer.lower()

    assert "concentration" in lowered
    assert "idiosyncratic" in lowered

    assert (
        "does not inherently mean a lower expected return"
        in lowered
    )


def test_q23_no_unsupported_diversification_taxonomy():

    answer = repair(
        "Explain idiosyncratic risk and why diversification "
        "can reduce it."
    )

    lowered = answer.lower()

    assert "company-specific" in lowered
    assert "systematic market risk" in lowered

    assert "diagonal diversification" not in lowered
    assert "style diversification" not in lowered


def test_q26_correct_atmospheric_scattering():

    answer = repair(
        "Explain in plain English why the sky appears blue "
        "during the day."
    )

    lowered = answer.lower()

    assert "rayleigh scattering" in lowered
    assert "much more atmosphere" in lowered
    assert "red and orange" in lowered
    assert "wavelength-dependent scattering" in lowered


def test_q39_physics_momentum_not_energy():

    answer = repair(
        "Explain momentum in physics briefly, then explain why "
        "that is not the same subject as NeuroVest Price-momentum."
    )

    lowered = answer.lower()

    assert "p = m × v" in answer
    assert "not the same thing as energy" in lowered
    assert "price-momentum" in lowered


def test_q40_async_answer_bounded_to_requested_strategy():

    answer = repair(
        "If I ask about Python async code and also mention "
        "SSRN_3247865_053, should the answer become a "
        "strategy-library dump? Explain the coding issue while "
        "keeping the strategy reference separate."
    )

    lowered = answer.lower()

    assert "coroutine object" in lowered
    assert "await" in lowered
    assert "event loop" in lowered
    assert "ssrn_3247865_053" in lowered
    assert "price-momentum" in lowered

    assert "five strategies" not in lowered

    assert (
        "strong structured model lineage"
        not in lowered
    )


def test_unrelated_response_remains_unchanged():

    original = (
        "Water freezes at its freezing point under "
        "the stated conditions."
    )

    result = repair(
        "Why does water freeze?",
        original,
    )

    assert result == original
