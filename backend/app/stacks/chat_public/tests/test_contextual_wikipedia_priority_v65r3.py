"""V65R3: contextual follow-up routing regressions."""

from types import SimpleNamespace

import pytest

from backend.app.stacks.chat_public import chat_runtime
from backend.app.stacks.chat_public.knowledge_tools.wikipedia_lookup import (
    WikipediaArticle,
)

CONTEXT = """
THREAD SUMMARY:
Northern Wolf was originally mean-reversion using RSI
and Bollinger Bands. It was corrected to momentum using
MACD and EMA crossovers.
""".strip()


def intent():
    return SimpleNamespace(
        blocked=False,
        intent="general_conversation",
        symbol=None,
        subtype=None,
    )


@pytest.mark.parametrize("question", [
    "What is Northern Wolf now, and which indicators did I replace?",
    "What is Northern Wolf currently?",
    "What is Northern Wolf now?",
    "What is my strategy now?",
    "What is our strategy currently?",
    "What is Northern Wolf as we discussed?",
    "What is Northern Wolf currently, as discussed?",
    "What is Northern Wolf currently standing at?",
])
def test_followup_uses_model(monkeypatch, question):
    calls = []

    def forbidden_wiki(*args, **kwargs):
        pytest.fail("Contextual follow-up reached Wikipedia")

    def fake_model(message, **kwargs):
        calls.append(kwargs)
        return (
            "Northern Wolf is momentum using MACD and EMA "
            "crossovers, replacing RSI and Bollinger Bands."
        )

    monkeypatch.setattr(
        chat_runtime, "lookup_wikipedia_article", forbidden_wiki
    )
    monkeypatch.setattr(
        chat_runtime, "ask_ollama", fake_model
    )

    result = chat_runtime.handle_chat_message(
        question,
        model_input=CONTEXT,
        detected_intent=intent(),
    )

    assert result["status"] == "ok"
    assert result["provider"] == "ollama"
    assert calls
    assert calls[0]["context"].startswith(CONTEXT)
    assert "MACD" in result["response"]["message"]


def test_standalone_wikipedia_preserved(monkeypatch):
    calls = []

    def wiki(topic, use_cache=True):
        calls.append(topic)
        return WikipediaArticle(
            title="Dire wolf",
            summary="The dire wolf is an extinct canine.",
            url="https://en.wikipedia.org/wiki/Dire_wolf",
        )

    monkeypatch.setattr(
        chat_runtime, "lookup_wikipedia_article", wiki
    )

    result = chat_runtime.handle_chat_message(
        "What is a dire wolf?",
        model_input=CONTEXT,
        detected_intent=intent(),
    )

    assert result["provider"] == "wikipedia"
    assert calls == ["a dire wolf"]


def test_explicit_wikipedia_preserved(monkeypatch):
    calls = []

    def wiki(topic, use_cache=True):
        calls.append(topic)
        return WikipediaArticle(
            title="Northern Wolf",
            summary="Synthetic encyclopedia content.",
            url="https://en.wikipedia.org/wiki/Wolf",
        )

    monkeypatch.setattr(
        chat_runtime, "lookup_wikipedia_article", wiki
    )

    result = chat_runtime.handle_chat_message(
        "What is Northern Wolf on Wikipedia?",
        model_input=CONTEXT,
        detected_intent=intent(),
    )

    assert result["provider"] == "wikipedia"
    assert len(calls) == 1


def test_no_context_retains_existing_wikipedia_behavior(monkeypatch):
    calls = []

    def wiki(topic, use_cache=True):
        calls.append(topic)
        return WikipediaArticle(
            title="Northern Wolf",
            summary="Synthetic encyclopedia content.",
            url="https://en.wikipedia.org/wiki/Wolf",
        )

    monkeypatch.setattr(
        chat_runtime, "lookup_wikipedia_article", wiki
    )

    result = chat_runtime.handle_chat_message(
        "What is Northern Wolf currently?",
        model_input=None,
        detected_intent=intent(),
    )

    assert result["provider"] == "wikipedia"
    assert len(calls) == 1


def test_existing_v2_contract_retained():
    from pathlib import Path

    source = Path(chat_runtime.__file__).read_text(
        encoding="utf-8"
    )

    assert "NEUROVEST_RESPONSE_ROUTING_REPAIR_V2" in source
    assert "NEUROVEST_V65R3_CONTEXTUAL_FOLLOWUP_PRIORITY" in source
    assert "extract_wikipedia_topic(message)" in source
    assert "not _specialized_explanation" in source
    assert "not _nv_g40_multi_part_explanation" in source
    assert "or _explicit_wiki" in source
