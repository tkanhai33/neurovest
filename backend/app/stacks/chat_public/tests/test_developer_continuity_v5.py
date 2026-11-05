import pytest

from backend.app.stacks.chat_public.developer_continuity_v5 import (
    continuation_question,
)


@pytest.mark.parametrize("followup", [
    "Which functions are responsible?",
    "Okay, how would we improve that?",
    "Why does it work that way?",
    "Can you trace that?",
    "What should we improve?",
])
def test_technical_continuations(followup):
    result = continuation_question(
        message=followup,
        previous_user="Neuro, inspect our chat routing.",
        verified_developer=True,
    )
    assert result is not None
    assert "chat routing" in result
    assert "Follow-up question:" in result


@pytest.mark.parametrize("previous", [
    "Explain how paper trading works.",
    "What stocks should I buy?",
    "Tell me about the weather.",
])
def test_unrelated_topics(previous):
    assert continuation_question(
        message="Which functions are responsible?",
        previous_user=previous,
        verified_developer=True,
    ) is None


def test_unauthorized_continuation():
    assert continuation_question(
        message="Which functions are responsible?",
        previous_user="Inspect our chat routing.",
        verified_developer=False,
    ) is None


def test_explicit_commands_unmodified():
    assert continuation_question(
        message="/dev awareness explain architecture",
        previous_user="Inspect our repository architecture.",
        verified_developer=True,
    ) is None


def test_unanchored_followup_rejected():
    assert continuation_question(
        message="Tell me a joke.",
        previous_user="Inspect our chat routing.",
        verified_developer=True,
    ) is None


def test_oversized_history_rejected():
    assert continuation_question(
        message="Which functions are responsible?",
        previous_user="Inspect our chat routing. " + "x" * 2000,
        verified_developer=True,
    ) is None
