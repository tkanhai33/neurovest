from __future__ import annotations

from pathlib import Path
import ast

import pytest
from pydantic import ValidationError

from backend.app.stacks.chat_public.contracts.chat_contracts import (
    ChatResponse,
)


ROOT = Path(__file__).resolve().parents[5]

RUNTIME = (
    ROOT
    / "backend"
    / "app"
    / "stacks"
    / "chat_public"
    / "chat_runtime.py"
)

ALLOWED_TOOL_TRUTH_STATES = {
    "grounded",
    "partial",
    "ungrounded",
    "not_required",
}


def runtime_source() -> str:
    return RUNTIME.read_text(
        encoding="utf-8",
    )


def build_response(
    tool_truth_state: str,
) -> ChatResponse:
    return ChatResponse(
        status="ok",
        thread_id="truth-state-thread",
        user_message_id="truth-state-user",
        assistant_message_id="truth-state-assistant",
        message="Truth-state contract response.",
        tool_truth_state=tool_truth_state,
        evidence=[],
        metadata={},
    )


def test_response_contract_accepts_only_declared_truth_states() -> None:
    for value in ALLOWED_TOOL_TRUTH_STATES:
        response = build_response(
            value
        )

        assert (
            response.tool_truth_state
            == value
        )


def test_response_contract_rejects_retrieval_required() -> None:
    with pytest.raises(
        ValidationError
    ):
        build_response(
            "retrieval_required"
        )


def test_runtime_never_assigns_retrieval_required_as_truth_state() -> None:
    source = runtime_source()

    assert (
        "routing_decision.retrieval_required"
        in source
    )

    tree = ast.parse(
        source
    )

    invalid_assignments = []

    for node in ast.walk(tree):
        if not isinstance(
            node,
            (
                ast.Assign,
                ast.AnnAssign,
            ),
        ):
            continue

        targets = (
            node.targets
            if isinstance(
                node,
                ast.Assign,
            )
            else [node.target]
        )

        target_names = {
            target.id
            for target in targets
            if isinstance(
                target,
                ast.Name,
            )
        }

        if (
            "tool_truth_state"
            not in target_names
        ):
            continue

        for child in ast.walk(
            node.value
        ):
            if (
                isinstance(
                    child,
                    ast.Constant,
                )
                and child.value
                == "retrieval_required"
            ):
                invalid_assignments.append(
                    node.lineno
                )

    assert invalid_assignments == []


def test_retrieval_required_route_maps_to_ungrounded_truth() -> None:
    source = runtime_source()

    expected = (
        'tool_truth_state = (\n'
        '                "ungrounded"\n'
        '                if routing_decision.retrieval_required'
    )

    assert expected in source
