import ast
from pathlib import Path

import pytest

BASE = Path(__file__).resolve().parents[1]
SOURCE = BASE / "chat_runtime.py"


def load_classifier():
    tree = ast.parse(SOURCE.read_text("utf-8"))

    nodes = [
        n for n in tree.body
        if isinstance(n, ast.FunctionDef)
        and n.name == "_neuro_v41_auto_awareness_question"
    ]

    assert len(nodes) == 1

    module = ast.Module(
        body=nodes,
        type_ignores=[],
    )

    namespace = {}
    exec(
        compile(module, str(SOURCE), "exec"),
        namespace,
    )
    return namespace[
        "_neuro_v41_auto_awareness_question"
    ]


@pytest.mark.parametrize("question", [
    "Neuro, inspect our chat routing.",
    "Why is our chat handler returning that response?",
    "Review our developer chat commands.",
    "Explain NeuroVest's context retrieval pipeline.",
    "Inspect our repository architecture.",
    "Trace our backend module dependencies.",
    "How does our conversation engine work?",
    "Which functions are in our repository architecture?",
])
def test_developer_intent_recognized(question):
    result = load_classifier()(question, True)
    assert result is not None
    assert result.startswith(
        "/dev awareness explain "
    )


@pytest.mark.parametrize("question", [
    "Explain how paper trading works.",
    "What is a momentum trading strategy?",
    "How can I improve my portfolio allocation?",
    "Explain risk-adjusted returns.",
    "What is a financial model?",
    "What happens during a market correction?",
    "Hello Neuro.",
    "Which stocks are performing well?",
])
def test_general_discussion_not_hijacked(question):
    assert load_classifier()(question, True) is None


@pytest.mark.parametrize("question", [
    "Inspect our repository architecture.",
    "Neuro, inspect our chat routing.",
    "As your developer, review our chat handler.",
])
def test_unauthorized_requests_not_promoted(question):
    assert load_classifier()(question, False) is None


def test_slash_commands_not_rewritten():
    assert load_classifier()(
        "/dev awareness explain repository architecture",
        True,
    ) is None


def test_empty_and_oversized_messages_rejected():
    classifier = load_classifier()
    assert classifier("", True) is None
    assert classifier("x" * 3001, True) is None


def test_runtime_still_uses_authenticated_role():
    source = SOURCE.read_text("utf-8")
    assert "_v41_developer_role(principal)" in source
    assert "if not _v3_developer_role(principal)" in source
