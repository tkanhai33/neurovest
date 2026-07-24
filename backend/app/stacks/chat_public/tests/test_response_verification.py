from __future__ import annotations

import ast
from pathlib import Path

from backend.app.stacks.chat_public.math_tools.live_math import (
    LiveMathBundle,
    evaluate_live_math,
)
from backend.app.stacks.chat_public.rag.live_retrieval import (
    LiveRetrievalBundle,
)
from backend.app.stacks.chat_public.response_verification import (
    verify_response,
)


def no_math() -> LiveMathBundle:
    return LiveMathBundle(
        requested=False,
        extracted=False,
        succeeded=False,
        operation=None,
        arguments={},
        result=None,
        prompt_section="",
        error=None,
    )


def no_retrieval() -> LiveRetrievalBundle:
    return LiveRetrievalBundle(
        requested=False,
        results=(),
        prompt_section="",
        citations=(),
        error=None,
    )


def retrieval_bundle() -> LiveRetrievalBundle:
    return LiveRetrievalBundle(
        requested=True,
        results=(),
        prompt_section="",
        citations=(
            {
                "citation":
                    "[chunk_allowed_1]",
                "chunk_id":
                    "chunk_allowed_1",
                "document_id":
                    "doc-1",
                "source_path":
                    "knowledge/research/example.pdf",
                "title":
                    "Example Research",
                "page_number":
                    12,
                "score":
                    0.9,
            },
        ),
        error=None,
    )


def test_ordinary_response_passes() -> None:
    result = verify_response(
        "Neuro is online.",
        math_bundle=no_math(),
        retrieval_bundle=no_retrieval(),
    )

    assert result.passed is True
    assert result.repaired is False
    assert result.final_response == (
        "Neuro is online."
    )


def test_exact_math_result_passes() -> None:
    math = evaluate_live_math(
        "What is 17.5 percent of 2480?",
        requested=True,
    )

    result = verify_response(
        (
            "17.5 percent of 2480 is exactly "
            "434.000."
        ),
        math_bundle=math,
        retrieval_bundle=no_retrieval(),
    )

    assert result.passed is True
    assert result.repaired is False


def test_decimal_equivalent_math_result_passes() -> None:
    math = evaluate_live_math(
        "What is 17.5 percent of 2480?",
        requested=True,
    )

    result = verify_response(
        "The result is 434.",
        math_bundle=math,
        retrieval_bundle=no_retrieval(),
    )

    assert result.passed is True


def test_missing_math_result_is_repaired() -> None:
    math = evaluate_live_math(
        "What is 17.5 percent of 2480?",
        requested=True,
    )

    result = verify_response(
        "The result is easy to calculate.",
        math_bundle=math,
        retrieval_bundle=no_retrieval(),
    )

    assert result.passed is False
    assert result.repaired is True
    assert result.fail_closed is True
    assert "434" in result.final_response

    codes = {
        violation.code
        for violation
        in result.violations
    }

    assert (
        "deterministic_math_value_missing"
        in codes
    )


def test_position_size_result_passes() -> None:
    math = evaluate_live_math(
        (
            "Calculate position size with account value 25000, "
            "risk 1 percent, entry 52.50, stop 50.00."
        ),
        requested=True,
    )

    result = verify_response(
        (
            "The risk budget is 250 and the whole-unit "
            "position size is 100 shares."
        ),
        math_bundle=math,
        retrieval_bundle=no_retrieval(),
    )

    assert result.passed is True


def test_allowed_citation_passes() -> None:
    retrieval = retrieval_bundle()

    result = verify_response(
        (
            "The evidence supports the explanation "
            "[chunk_allowed_1]."
        ),
        math_bundle=no_math(),
        retrieval_bundle=retrieval,
    )

    assert result.passed is True
    assert result.repaired is False


def test_missing_required_citation_is_repaired() -> None:
    retrieval = retrieval_bundle()

    result = verify_response(
        "The research supports this conclusion.",
        math_bundle=no_math(),
        retrieval_bundle=retrieval,
    )

    assert result.passed is False
    assert result.repaired is True
    assert result.fail_closed is True

    assert (
        "[chunk_allowed_1]"
        in result.final_response
    )


def test_unapproved_citation_is_repaired() -> None:
    retrieval = retrieval_bundle()

    result = verify_response(
        (
            "This is supported by "
            "[chunk_invented_999]."
        ),
        math_bundle=no_math(),
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

    assert "unapproved_citation" in codes
    assert (
        "[chunk_invented_999]"
        not in result.final_response
    )


def test_live_execution_claim_fails_closed() -> None:
    result = verify_response(
        (
            "Live broker execution is enabled, "
            "and I can place real orders."
        ),
        math_bundle=no_math(),
        retrieval_bundle=no_retrieval(),
    )

    assert result.passed is False
    assert result.repaired is True
    assert result.fail_closed is True

    assert (
        "Live-money broker execution remains disabled"
        in result.final_response
    )


def test_safe_live_execution_denial_passes() -> None:
    result = verify_response(
        (
            "Live execution remains locked. "
            "I can help with paper-trading analysis."
        ),
        math_bundle=no_math(),
        retrieval_bundle=no_retrieval(),
    )

    assert result.passed is True


def test_empty_response_fails_closed() -> None:
    result = verify_response(
        "   ",
        math_bundle=no_math(),
        retrieval_bundle=no_retrieval(),
    )

    assert result.passed is False
    assert result.repaired is True
    assert result.fail_closed is True
    assert result.final_response


def test_result_serialization_is_structured() -> None:
    result = verify_response(
        "Neuro is online.",
        math_bundle=no_math(),
        retrieval_bundle=no_retrieval(),
    )

    payload = result.as_dict()

    assert payload[
        "status"
    ] == "passed"

    assert payload[
        "checks"
    ][
        "paper_only_boundary_valid"
    ] is True

    assert isinstance(
        payload[
            "violations"
        ],
        list,
    )


def test_verifier_has_no_external_authority() -> None:
    path = Path(
        "backend/app/stacks/chat_public/"
        "response_verification.py"
    )

    tree = ast.parse(
        path.read_text(
            encoding="utf-8"
        )
    )

    forbidden_import_roots = {
        "asyncio",
        "httpx",
        "requests",
        "socket",
        "sqlalchemy",
        "subprocess",
        "urllib",
    }

    forbidden_name_calls = {
        "eval",
        "exec",
        "compile",
        "__import__",
    }

    forbidden_authority_calls = {
        "place_order",
        "submit_order",
        "execute_order",
        "send_order",
        "add_tool_evidence",
        "append_message",
    }

    for node in ast.walk(
        tree
    ):
        if isinstance(
            node,
            ast.Import,
        ):
            for alias in node.names:
                root = alias.name.split(
                    "."
                )[0]

                assert (
                    root
                    not in forbidden_import_roots
                )

        if isinstance(
            node,
            ast.ImportFrom,
        ):
            module = (
                node.module
                or ""
            )

            root = module.split(
                "."
            )[0]

            assert (
                root
                not in forbidden_import_roots
            )

        if isinstance(
            node,
            ast.Call,
        ):
            if isinstance(
                node.func,
                ast.Name,
            ):
                assert (
                    node.func.id
                    not in forbidden_name_calls
                )

            if isinstance(
                node.func,
                ast.Attribute,
            ):
                assert (
                    node.func.attr
                    not in forbidden_authority_calls
                )
