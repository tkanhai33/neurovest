from __future__ import annotations

import inspect

from backend.app.stacks.chat_public import (
    chat_runtime,
)
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


def test_verifier_replaces_missing_math_result() -> None:
    math = evaluate_live_math(
        "What is 17.5 percent of 2480?",
        requested=True,
    )

    result = verify_response(
        "That is straightforward.",
        math_bundle=math,
        retrieval_bundle=no_retrieval(),
    )

    assert result.passed is False
    assert result.repaired is True
    assert result.fail_closed is True
    assert "434" in result.final_response


def test_verifier_preserves_exact_math_result() -> None:
    math = evaluate_live_math(
        "What is 17.5 percent of 2480?",
        requested=True,
    )

    result = verify_response(
        "The exact answer is 434.",
        math_bundle=math,
        retrieval_bundle=no_retrieval(),
    )

    assert result.passed is True
    assert result.repaired is False
    assert result.final_response == (
        "The exact answer is 434."
    )


def test_verifier_replaces_live_execution_claim() -> None:
    result = verify_response(
        (
            "Live broker execution is enabled, "
            "and I can place real trades."
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


def test_runtime_verification_occurs_before_persistence() -> None:
    source = inspect.getsource(
        chat_runtime.run_chat_turn
    )

    content_position = source.find(
        "assistant_content = _response_message("
    )

    verification_position = source.find(
        "verification_result: ResponseVerificationResult",
        content_position,
    )

    replacement_position = source.find(
        "verification_result.final_response",
        verification_position,
    )

    persistence_position = source.find(
        "assistant_message = (",
        replacement_position,
    )

    assert content_position >= 0
    assert verification_position > content_position
    assert replacement_position > verification_position
    assert persistence_position > replacement_position


def test_runtime_emits_verification_event() -> None:
    source = inspect.getsource(
        chat_runtime.run_chat_turn
    )

    assert (
        'event_type="RESPONSE_VERIFICATION_COMPLETED"'
        in source
    )

    assert (
        '"verification_status"'
        in source
    )

    assert (
        "verification_result.violations"
        in source
    )


def test_runtime_persists_verification_evidence() -> None:
    source = inspect.getsource(
        chat_runtime.run_chat_turn
    )

    assert (
        'tool_name="response_verification"'
        in source
    )

    assert (
        "verification_evidence = ToolEvidence("
        in source
    )

    assert (
        "conversation_store.add_tool_evidence("
        in source
    )

    assert (
        "current_turn_evidence.append("
        in source
    )

    assert (
        "assistant_message.message_id"
        in source
    )


def test_runtime_exposes_verification_metadata() -> None:
    source = inspect.getsource(
        chat_runtime.run_chat_turn
    )

    required = (
        '"verification_status"',
        '"verification_passed"',
        '"verification_repaired"',
        '"verification_fail_closed"',
        '"verification_checks"',
        '"verification_violations"',
    )

    for marker in required:
        assert marker in source
