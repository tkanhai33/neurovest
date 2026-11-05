from types import SimpleNamespace

from backend.app.stacks.chat_public import chat_runtime
from backend.app.stacks.chat_public.knowledge_tools.wikipedia_lookup import (
    WikipediaArticle,
    extract_wikipedia_topic,
)


def test_extracts_general_wikipedia_topic() -> None:
    assert (
        extract_wikipedia_topic("What is a black hole?")
        == "a black hole"
    )

    assert extract_wikipedia_topic(
        "What is the current stock price of NVDA?"
    ) is None


def test_wikipedia_answer_is_grounded_without_link(
    monkeypatch,
) -> None:
    article = WikipediaArticle(
        title="Black hole",
        summary=(
            "A black hole is a region of spacetime where "
            "gravity is so strong that nothing can escape."
        ),
        url="https://en.wikipedia.org/wiki/Black_hole",
    )

    monkeypatch.setattr(
        chat_runtime,
        "lookup_wikipedia_article",
        lambda topic, use_cache: article,
    )

    intent = SimpleNamespace(
        blocked=False,
        intent="trading_conversation",
        symbol=None,
    )

    result = chat_runtime.handle_chat_message(
        "What is a black hole?",
        detected_intent=intent,
    )

    message = result["response"]["message"]

    assert result["status"] == "ok"
    assert result["provider"] == "wikipedia"
    assert result["model"] is None
    assert result["tool_truth_state"] == "grounded"
    assert "gravity is so strong" in message
    assert "Wikipedia" not in message
    assert "https://" not in message


def test_wikipedia_link_is_shown_only_when_requested(
    monkeypatch,
) -> None:
    article = WikipediaArticle(
        title="Black hole",
        summary="A black hole is an astronomical object.",
        url="https://en.wikipedia.org/wiki/Black_hole",
    )

    monkeypatch.setattr(
        chat_runtime,
        "lookup_wikipedia_article",
        lambda topic, use_cache: article,
    )

    intent = SimpleNamespace(
        blocked=False,
        intent="trading_conversation",
        symbol=None,
    )

    result = chat_runtime.handle_chat_message(
        "What is a black hole? Source",
        detected_intent=intent,
    )

    assert "[Wikipedia — Black hole]" in (
        result["response"]["message"]
    )
