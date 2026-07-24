from __future__ import annotations

import ast
import asyncio
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

from backend.app.stacks.chat_public.chat_runtime import (
    handle_chat_message,
)

from backend.app.stacks.chat_public.context import (
    context_assembler,
)

from backend.app.stacks.chat_public.role_overlay_registry import (
    render_role_overlay,
    resolve_role_overlay,
)


ROOT = Path(__file__).resolve().parents[5]

CHAT_API = (
    ROOT
    / "backend/app/stacks/chat_public/chat_api.py"
)

CHAT_RUNTIME = (
    ROOT
    / "backend/app/stacks/chat_public/chat_runtime.py"
)


def _call_name(
    node: ast.Call,
) -> str | None:
    if isinstance(node.func, ast.Name):
        return node.func.id

    if isinstance(node.func, ast.Attribute):
        return node.func.attr

    return None


def _fake_bundle() -> dict[str, object]:
    return {
        "conversation_state": SimpleNamespace(
            summary="",
            remembered_terms={},
            active_strategy=None,
            portfolio_context={},
        ),
        "memory_facts": [],
        "tool_evidence": [],
        "messages": [],
    }


def test_role_overlay_is_inserted_in_correct_order(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        context_assembler.conversation_store,
        "load_context_bundle",
        AsyncMock(
            return_value=_fake_bundle()
        ),
    )

    overlay = render_role_overlay(
        resolve_role_overlay(
            role="developer",
        )
    )

    result = asyncio.run(
        context_assembler.assemble_chat_context(
            thread_id="stage4d-thread",
            current_message="Hello Neuro.",
            intent_metadata={},
            role_overlay=overlay,
        )
    )

    assert "ROLE OVERLAY" in result.prompt

    assert (
        "Authorization role: developer"
        in result.prompt
    )

    assert (
        result.prompt.index("TRUTH BOUNDARY")
        < result.prompt.index("ROLE OVERLAY")
        < result.prompt.index("THREAD SUMMARY")
    )


def test_no_overlay_path_remains_supported(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        context_assembler.conversation_store,
        "load_context_bundle",
        AsyncMock(
            return_value=_fake_bundle()
        ),
    )

    result = asyncio.run(
        context_assembler.assemble_chat_context(
            thread_id="stage4d-thread",
            current_message="Hello Neuro.",
            intent_metadata={},
        )
    )

    assert "ROLE OVERLAY" not in result.prompt
    assert "SYSTEM ROLE" in result.prompt
    assert "TRUTH BOUNDARY" in result.prompt


def test_chat_api_passes_principal_to_runtime() -> None:
    tree = ast.parse(
        CHAT_API.read_text(
            encoding="utf-8"
        )
    )

    calls = [
        node
        for node in ast.walk(tree)
        if (
            isinstance(node, ast.Call)
            and _call_name(node)
            == "run_chat_turn"
        )
    ]

    assert len(calls) == 1

    principal_keywords = [
        keyword
        for keyword in calls[0].keywords
        if keyword.arg == "principal"
    ]

    assert len(principal_keywords) == 1

    assert isinstance(
        principal_keywords[0].value,
        ast.Name,
    )

    assert (
        principal_keywords[0].value.id
        == "principal"
    )


def test_runtime_passes_overlay_and_intent_metadata() -> None:
    tree = ast.parse(
        CHAT_RUNTIME.read_text(
            encoding="utf-8"
        )
    )

    function = next(
        node
        for node in tree.body
        if (
            isinstance(
                node,
                ast.AsyncFunctionDef,
            )
            and node.name == "run_chat_turn"
        )
    )

    calls = [
        node
        for node in ast.walk(function)
        if (
            isinstance(node, ast.Call)
            and _call_name(node)
            == "assemble_chat_context"
        )
    ]

    assert len(calls) == 1

    keyword_names = {
        keyword.arg
        for keyword in calls[0].keywords
    }

    assert "intent_metadata" in keyword_names
    assert "role_overlay" in keyword_names


def test_unknown_role_fails_closed_to_user_overlay() -> None:
    overlay = render_role_overlay(
        resolve_role_overlay(
            role="untrusted_superuser",
        )
    )

    assert "Authorization role: user" in overlay

    assert (
        "Repository context permitted: False"
        in overlay
    )

    assert (
        "Administrative context permitted: False"
        in overlay
    )


def test_deterministic_developer_path_remains_grounded() -> None:
    result = handle_chat_message(
        "As your developer, what capabilities "
        "are currently available?",
        developer_evidence_allowed=True,
    )

    assert result["status"] == "ok"

    assert (
        result["provider"]
        == "neurovest_local_evidence"
    )

    assert result["model"] is None

    assert (
        result["tool_truth_state"]
        == "grounded"
    )
