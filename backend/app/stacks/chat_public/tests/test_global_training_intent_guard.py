
"""Global training classification must never imply authorization."""

import pytest

from backend.app.stacks.chat_public.global_training_intent_guard import (
    classify_global_training_request,
)


@pytest.mark.parametrize(
    "message",
    [
        "Run a system wide training session.",
        "Start global training from my normal account.",
        "Please initiate system-level training.",
        "Launch training for the global profile.",
    ],
)
def test_direct_execution_requests(message):
    result = classify_global_training_request(message)

    assert result.classification == (
        "global_training_execution_request"
    )
    assert result.execution_requested is True


@pytest.mark.parametrize(
    "message",
    [
        "Don't start global training.",
        "Do not run a system-wide training session.",
        "Never launch training for the global profile.",
    ],
)
def test_negated_requests_never_execute(message):
    result = classify_global_training_request(message)

    assert result.execution_requested is False
    assert result.classification == "negated_global_training"


@pytest.mark.parametrize(
    "message",
    [
        "Can you explain what global training does?",
        "What would happen if I started system training?",
        "Explain system-wide training.",
        "How does global training work?",
    ],
)
def test_discussion_never_executes(message):
    result = classify_global_training_request(message)

    assert result.execution_requested is False


@pytest.mark.parametrize(
    "message",
    [
        "Train on my connected SnapTrade stocks.",
        "Explain an ETF.",
        "Why was my reward negative?",
        "Help me study Python.",
    ],
)
def test_unrelated_messages_not_global_training(message):
    result = classify_global_training_request(message)

    assert result.classification == "not_global_training"
    assert result.execution_requested is False


def test_ambiguous_global_training_fails_closed():
    result = classify_global_training_request(
        "Global training for the strategy profile"
    )

    assert result.execution_requested is False


def test_global_training_chat_boundary_v1():
    from backend.app.stacks.chat_public.global_training_intent_guard import (
        global_training_chat_reply,
    )

    request = "Run a system wide training session."

    ordinary = global_training_chat_reply(
        request,
        developer_context_allowed=False,
    )

    developer = global_training_chat_reply(
        request,
        developer_context_allowed=True,
    )

    assert ordinary is not None
    assert "restricted" in ordinary.lower()
    assert "No training was started" in ordinary

    assert developer is not None
    assert "does not by itself authorize" in developer
    assert "No training was started" in developer

    for message in (
        "Don't start global training.",
        "Explain how global training works.",
        "Train on my connected SnapTrade stocks.",
        "Why was my reward negative?",
    ):
        assert global_training_chat_reply(
            message,
            developer_context_allowed=False,
        ) is None


def test_global_training_runtime_boundary_precedence_v1():
    from pathlib import Path
    import ast

    runtime = (
        Path(__file__).resolve().parents[1]
        / "chat_runtime.py"
    )

    source = runtime.read_text(encoding="utf-8")
    tree = ast.parse(source)

    assert (
        "NEUROVEST_GLOBAL_TRAINING_CHAT_BOUNDARY_V1"
        in source
    )
    assert (
        source.index("if _global_training_reply is not None:")
        < source.index(
            "elif _contextual_training_reply is not None:"
        )
    )

    assert tree is not None
