from __future__ import annotations

import json

from backend.app.stacks.chat_public import ollama_chat_client


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return json.dumps(
            {"message": {"content": "grounded reply"}}
        ).encode("utf-8")


def test_conversation_relevance_reaches_ollama(
    monkeypatch,
) -> None:
    captured = {}

    def fake_urlopen(request, timeout):
        captured["request"] = request
        return FakeResponse()

    monkeypatch.setattr(
        ollama_chat_client.urllib.request,
        "urlopen",
        fake_urlopen,
    )

    ollama_chat_client.ask_ollama(
        "How does that apply if a portfolio is concentrated in one industry?",
        context="Earlier discussion: diversification and market-wide risk.",
        model="neuro-reason:latest",
    )

    payload = json.loads(captured["request"].data.decode("utf-8"))
    system_message = payload["messages"][0]["content"]

    assert "CONVERSATION RELEVANCE" in system_message
    assert "Answer the current user message directly" in system_message
    assert "must not assume momentum investing" in system_message
