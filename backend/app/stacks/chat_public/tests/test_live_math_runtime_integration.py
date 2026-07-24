from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from backend.app.stacks.chat_public import (
    chat_runtime,
)
from backend.app.stacks.chat_public.math_tools.live_math import (
    evaluate_live_math,
    extract_math_request,
)


@pytest.mark.parametrize(
    (
        "message",
        "operation",
    ),
    [
        (
            "What is 17.5 percent of 2480?",
            "percentage_of",
        ),
        (
            "Calculate the percentage change from 80 to 100.",
            "percent_change",
        ),
        (
            "Calculate CAGR from 10000 to 16500 over 5 years.",
            "cagr",
        ),
        (
            (
                "Calculate position size with account value 25000, "
                "risk 1 percent, entry 52.50, stop 50.00."
            ),
            "position_size",
        ),
        (
            (
                "Calculate risk reward with entry 50, "
                "stop 48, target 56."
            ),
            "risk_reward",
        ),
        (
            (
                "Calculate compound return, returns: "
                "10%, -5%, 8%."
            ),
            "compound_return",
        ),
        (
            (
                "Calculate maximum drawdown from equity curve: "
                "100, 120, 90, 95, 80, 130."
            ),
            "maximum_drawdown",
        ),
        (
            "Calculate 1250 * 0.08.",
            "arithmetic",
        ),
    ],
)
def test_supported_math_requests_are_extracted(
    message: str,
    operation: str,
) -> None:
    extracted = extract_math_request(
        message
    )

    assert extracted is not None
    assert (
        extracted.request.operation
        == operation
    )


def test_percentage_result_is_exact() -> None:
    bundle = evaluate_live_math(
        "What is 17.5 percent of 2480?",
        requested=True,
    )

    assert bundle.requested is True
    assert bundle.extracted is True
    assert bundle.succeeded is True
    assert bundle.grounded is True
    assert bundle.operation == "percentage_of"
    assert bundle.result is not None

    assert (
        bundle.result[
            "values"
        ][
            "result"
        ]
        == "434.000"
    )

    assert (
        "authoritative"
        in bundle.prompt_section
    )


def test_cagr_result_is_deterministic() -> None:
    message = (
        "Calculate CAGR from 10000 "
        "to 16500 over 5 years."
    )

    first = evaluate_live_math(
        message,
        requested=True,
    )

    second = evaluate_live_math(
        message,
        requested=True,
    )

    assert first.grounded
    assert second.grounded
    assert first.result == second.result


def test_position_size_uses_whole_units() -> None:
    bundle = evaluate_live_math(
        (
            "Calculate position size with account value 25000, "
            "risk 1 percent, entry 52.50, stop 50.00."
        ),
        requested=True,
    )

    assert bundle.grounded
    assert bundle.result is not None

    assert (
        bundle.result[
            "values"
        ][
            "quantity"
        ]
        == "100"
    )


def test_unrequested_math_does_not_execute() -> None:
    bundle = evaluate_live_math(
        "What is 2 + 2?",
        requested=False,
    )

    assert bundle.requested is False
    assert bundle.extracted is False
    assert bundle.result is None
    assert bundle.prompt_section == ""


def test_ambiguous_math_fails_controlled() -> None:
    bundle = evaluate_live_math(
        "Calculate my portfolio risk.",
        requested=True,
    )

    assert bundle.requested is True
    assert bundle.extracted is False
    assert bundle.grounded is False
    assert bundle.result is None
    assert bundle.error is not None

    assert (
        "could not be extracted safely"
        in bundle.error
    )


def test_division_by_zero_returns_error_evidence() -> None:
    bundle = evaluate_live_math(
        "Calculate 10 / 0.",
        requested=True,
    )

    assert bundle.extracted is True
    assert bundle.succeeded is False
    assert bundle.grounded is False
    assert bundle.result is not None
    assert bundle.error is not None

    assert (
        "Division by zero"
        in bundle.error
    )


def test_runtime_contains_math_integration() -> None:
    source = inspect.getsource(
        chat_runtime.run_chat_turn
    )

    required = (
        "evaluate_live_math(",
        "routing_decision",
        ".deterministic_tool_required",
        "math_bundle.prompt_section",
        "deterministic_math_engine",
        "conversation_store.add_tool_evidence(",
        "math_bundle.result",
        '"math_result"',
    )

    for marker in required:
        assert marker in source


def test_live_math_has_no_arbitrary_execution() -> None:
    import ast

    path = Path(
        "backend/app/stacks/chat_public/"
        "math_tools/live_math.py"
    )

    source = path.read_text(
        encoding="utf-8",
    )

    tree = ast.parse(
        source
    )

    forbidden_name_calls = {
        "eval",
        "exec",
        "compile",
        "__import__",
    }

    forbidden_import_roots = {
        "asyncio",
        "httpx",
        "requests",
        "socket",
        "sqlalchemy",
        "subprocess",
        "urllib",
    }

    forbidden_authority_calls = {
        "place_order",
        "submit_order",
        "execute_order",
        "send_order",
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
