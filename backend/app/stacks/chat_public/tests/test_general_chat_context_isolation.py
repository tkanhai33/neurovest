from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from backend.app.stacks.chat_public.context import (
    context_assembler,
)


def _bundle() -> dict[str, object]:
    return {
        "conversation_state": SimpleNamespace(
            summary="",
            remembered_terms={},
            active_strategy=None,
            portfolio_context={
                "value_cad": 416.75,
                "symbol": "TD.TO",
            },
        ),
        "memory_facts": [],
        "tool_evidence": [],
        "messages": [],
        "learned_strategy_knowledge": [
            {
                "strategy_name": "Unrelated Strategy Context",
            },
        ],
        "enabled_reference_strategies": [
            {
                "strategy_name": "Reference Strategy Context",
            },
        ],
    }


def _assemble(monkeypatch, *, message: str, family: str):
    monkeypatch.setattr(
        context_assembler.conversation_store,
        "load_context_bundle",
        AsyncMock(return_value=_bundle()),
    )

    return asyncio.run(
        context_assembler.assemble_chat_context(
            thread_id="context-isolation-thread",
            current_message=message,
            intent_metadata={
                "intent": "general_conversation",
                "family": family,
            },
        )
    )


def test_general_greeting_excludes_unrelated_domain_context(
    monkeypatch,
) -> None:
    result = _assemble(
        monkeypatch,
        message="Hello Neuro.",
        family="GENERAL",
    )

    assert "LEARNED STRATEGY KNOWLEDGE" not in result.prompt
    assert "ENABLED REFERENCE STRATEGY LIBRARY" not in result.prompt
    assert "PORTFOLIO CONTEXT" not in result.prompt
    assert "Unrelated Strategy Context" not in result.prompt
    assert "Reference Strategy Context" not in result.prompt
    assert "TD.TO" not in result.prompt


def test_strategy_request_receives_strategy_context(
    monkeypatch,
) -> None:
    result = _assemble(
        monkeypatch,
        message="Explain this strategy.",
        family="STRATEGY",
    )

    assert "LEARNED STRATEGY KNOWLEDGE" in result.prompt
    assert "ENABLED REFERENCE STRATEGY LIBRARY" in result.prompt


def test_portfolio_request_receives_portfolio_context(
    monkeypatch,
) -> None:
    result = _assemble(
        monkeypatch,
        message="What is in my portfolio?",
        family="PORTFOLIO",
    )

    assert "PORTFOLIO CONTEXT" in result.prompt
    assert "TD.TO" in result.prompt
