from __future__ import annotations

import json

from backend.app.stacks.chat_public import (
    ollama_chat_client,
)


class FakeResponse:

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        return False

    def read(self):
        return json.dumps(
            {
                "message": {
                    "content": "grounded reply",
                },
            }
        ).encode("utf-8")


def test_financial_fact_grounding_reaches_ollama(
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

    result = ollama_chat_client.ask_ollama(
        (
            "What if nearly all of my portfolio is "
            "in two Canadian bank stocks?"
        ),
        model="neuro-reason:latest",
    )

    payload = json.loads(
        captured["request"].data.decode("utf-8")
    )

    system_message = payload["messages"][0]["content"]

    assert result == "grounded reply"
    assert "FINANCIAL FACT GROUNDING" in system_message
    assert "Never invent, assume, or name holdings" in system_message
    assert "answer generically" in system_message
