import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from backend.app.stacks.chat_public.context import (
    context_assembler as ca,
)


def m(role, content):
    return SimpleNamespace(role=role, content=content)


def make_bundle(messages):
    return {
        "conversation_state": SimpleNamespace(
            summary="",
            remembered_terms={},
            active_entities={},
            active_strategy=None,
            portfolio_context={},
        ),
        "memory_facts": [],
        "tool_evidence": [],
        "messages": messages,
        "learned_strategy_knowledge": [],
        "enabled_reference_strategies": [],
    }


def assemble(messages, question):
    loader = AsyncMock(return_value=make_bundle(messages))

    with patch.object(
        ca.conversation_store,
        "load_context_bundle",
        new=loader,
    ):
        result = asyncio.run(
            ca.assemble_chat_context(
                thread_id="v102-authorized-thread",
                current_message=question,
                intent_metadata={
                    "family": "GENERAL",
                    "intent": "general_conversation",
                },
            )
        )

    loader.assert_awaited_once()

    args, kwargs = loader.await_args

    assert args[0] == "v102-authorized-thread"
    assert kwargs["message_limit"] == 96

    return result


def test_v102_recalls_old_rust_decision():
    history = [
        m("user", "We chose Rust for our command-line project."),
        m("assistant", "Rust is the chosen project language."),
    ]

    for i in range(20):
        history.extend([
            m("user", f"Cooking question {i} about soup."),
            m("assistant", f"Cooking answer {i}."),
        ])

    result = assemble(
        history,
        "Back to our programming project, which language?",
    )

    assert "RELEVANT EARLIER CONVERSATION" in result.prompt
    assert "We chose Rust" in result.prompt
    assert "chosen project language" in result.prompt
    assert "Cooking question 19" in result.prompt
    assert result.recent_message_count == 16
    assert len(result.prompt) <= ca.MAX_PROMPT_CHARACTERS


def test_v102_does_not_insert_unrelated_old_topic():
    history = [
        m("user", "My private soup recipe uses carrots."),
        m("assistant", "We discussed the recipe."),
    ]

    for i in range(20):
        history.extend([
            m("user", f"Server debugging topic {i}."),
            m("assistant", f"Server debugging answer {i}."),
        ])

    result = assemble(
        history,
        "Explain the server debugging problem.",
    )

    assert "My private soup recipe" not in result.prompt
    assert "CURRENT USER MESSAGE" in result.prompt


def test_v102_short_chat_unchanged():
    history = [
        m("user", "Hello Neuro."),
        m("assistant", "Hello!"),
    ]

    result = assemble(history, "How are you?")

    assert "RELEVANT EARLIER CONVERSATION" not in result.prompt
    assert "USER: Hello Neuro." in result.prompt
    assert result.recent_message_count == 2


def test_v102_correction_stays_in_recent_history():
    history = [
        m("user", "Website theme is red."),
        m("assistant", "Red selected."),
    ]

    for i in range(10):
        history.extend([
            m("user", f"Unrelated question {i}."),
            m("assistant", f"Unrelated answer {i}."),
        ])

    history.extend([
        m("user", "Actually change the website theme to blue."),
        m("assistant", "Blue replaces red."),
    ])

    result = assemble(history, "Which website theme now?")

    assert "Actually change the website theme to blue." in result.prompt
    assert "Blue replaces red." in result.prompt
    assert "CURRENT USER MESSAGE" in result.prompt


def test_v102_prompt_keeps_truth_boundary():
    history = [
        m("user", "Rust is our project language."),
        m("assistant", "Agreed."),
    ]

    for i in range(50):
        history.extend([
            m("user", f"Other discussion {i} " + "x" * 300),
            m("assistant", f"Other answer {i} " + "y" * 300),
        ])

    result = assemble(history, "Back to our project language.")

    assert "TRUTH BOUNDARY" in result.prompt
    assert "CURRENT USER MESSAGE" in result.prompt
    assert "RESPONSE REQUIREMENTS" in result.prompt
    assert len(result.prompt) <= ca.MAX_PROMPT_CHARACTERS
