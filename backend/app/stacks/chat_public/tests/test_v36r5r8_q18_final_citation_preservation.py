from __future__ import annotations

from backend.app.stacks.chat_public.chat_runtime import (
    LiveRetrievalBundle,
    _ensure_approved_retrieval_citation,
    _v36r5_final_answer_quality_repair,
    evaluate_live_math,
)

from backend.app.stacks.chat_public.response_verification import (
    verify_response,
)


Q18 = (
    "What is the difference between NeuroVest "
    "/auth/logout and /auth/logout-all?"
)


APPROVED = (
    {
        "citation":
            "[chunk_v36r5r8_q18_test]",

        "chunk_id":
            "chunk_v36r5r8_q18_test",

        "document_id":
            "doc_v36r5r8_test",

        "source_path":
            "docs/test.md",

        "title":
            "V36-R5R8 Citation Contract Test",

        "page_number":
            None,

        "score":
            1.0,
    },
)


def retrieval_bundle() -> LiveRetrievalBundle:

    return LiveRetrievalBundle(
        requested=True,
        results=(),
        prompt_section="",
        citations=APPROVED,
        error=None,
        authoritative_grounding=True,
    )


def math_bundle():

    return evaluate_live_math(
        Q18,
        requested=False,
    )


def test_math_bundle_matches_real_non_math_request():

    bundle = math_bundle()

    assert bundle.requested is False
    assert bundle.grounded is False


def test_q18_semantic_repair_contains_correct_distinction():

    answer = _v36r5_final_answer_quality_repair(
        Q18,
        "placeholder",
    )

    lowered = answer.lower()

    assert "/auth/logout" in lowered
    assert "/auth/logout-all" in lowered
    assert "current authenticated session" in lowered
    assert "all active sessions" in lowered


def test_existing_helper_attaches_only_approved_token():

    answer = _v36r5_final_answer_quality_repair(
        Q18,
        "placeholder",
    )

    cited = _ensure_approved_retrieval_citation(
        answer,
        APPROVED,
    )

    assert (
        "[chunk_v36r5r8_q18_test]"
        in cited
    )


def test_cited_q18_passes_real_verifier_contract():

    retrieval = retrieval_bundle()
    math = math_bundle()

    answer = _v36r5_final_answer_quality_repair(
        Q18,
        "placeholder",
    )

    cited = _ensure_approved_retrieval_citation(
        answer,
        retrieval.citations,
    )

    result = verify_response(
        cited,
        math_bundle=math,
        retrieval_bundle=retrieval,
    )

    assert result.passed is True
    assert result.repaired is False
    assert result.fail_closed is False

    assert (
        result.checks[
            "citation_contract_valid"
        ]
        is True
    )

    assert (
        "[chunk_v36r5r8_q18_test]"
        in result.final_response
    )


def test_uncited_q18_still_fails_closed():

    retrieval = retrieval_bundle()
    math = math_bundle()

    answer = _v36r5_final_answer_quality_repair(
        Q18,
        "placeholder",
    )

    result = verify_response(
        answer,
        math_bundle=math,
        retrieval_bundle=retrieval,
    )

    assert result.passed is False
    assert result.repaired is True
    assert result.fail_closed is True

    codes = {
        violation.code
        for violation
        in result.violations
    }

    assert (
        "required_citation_missing"
        in codes
    )


def test_unapproved_citation_still_fails_closed():

    retrieval = retrieval_bundle()
    math = math_bundle()

    answer = (
        _v36r5_final_answer_quality_repair(
            Q18,
            "placeholder",
        )
        + "\n\n[chunk_NOT_APPROVED]"
    )

    result = verify_response(
        answer,
        math_bundle=math,
        retrieval_bundle=retrieval,
    )

    assert result.passed is False
    assert result.fail_closed is True

    codes = {
        violation.code
        for violation
        in result.violations
    }

    assert (
        "unapproved_citation"
        in codes
    )
