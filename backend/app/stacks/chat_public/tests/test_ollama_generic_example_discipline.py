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


def test_generic_example_discipline_reaches_ollama(
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
        "How does concentration in one industry affect a portfolio?",
        model="neuro-reason:latest",
    )

    payload = json.loads(captured["request"].data.decode("utf-8"))
    system_message = payload["messages"][0]["content"]

    assert "GENERIC EXAMPLE DISCIPLINE" in system_message
    assert "do not introduce unprompted company names" in system_message
    assert "subscription tiers" in system_message
    assert "Never assume the user has a free-tier account" in system_message
