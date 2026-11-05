
"""Regressions for finance explanations and training context."""

import pytest

from backend.app.stacks.db_runtime.contextual_training_intelligence import (
    is_training_followup,
)
from backend.app.stacks.chat_public.global_training_intent_guard import (
    classify_global_training_request,
)


@pytest.mark.parametrize(
    "question",
    [
        "Can you explain what would happen if I started system training?",
        "Explain how global training works.",
        "What is system-wide training?",
        "How does system-level learning work?",
        "Explain training for the global profile.",
    ],
)
def test_global_training_discussions_are_not_personal_followups(question):
    assert is_training_followup(question) is False


@pytest.mark.parametrize(
    "question",
    [
        "Why was my reward negative?",
        "How did my last training perform?",
        "Explain my training results.",
        "Which stock performed best in my training?",
    ],
)
def test_personal_training_followups_remain_active(question):
    assert is_training_followup(question) is True


def test_global_execution_request_remains_restricted():
    result = classify_global_training_request(
        "Run a system wide training session."
    )
    assert result.execution_requested is True


def test_wikipedia_guard_exists_in_runtime():
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "chat_runtime.py"
    source = path.read_text(encoding="utf-8")

    assert "NEUROVEST_RESPONSE_ROUTING_REPAIR_V2" in source
    assert "extract_wikipedia_topic(message)" in source
    assert "not _specialized_explanation" in source
    assert "not _nv_g40_multi_part_explanation" in source
    assert "or _explicit_wiki" in source
