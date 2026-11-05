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
                    "content": "qualified reply",
                },
            }
        ).encode("utf-8")


def test_context_is_system_reference_and_question_is_user_message(
    monkeypatch,
) -> None:
    captured = {}

    def fake_urlopen(
        request,
        timeout,
    ):
        captured["request"] = request
        return FakeResponse()

    monkeypatch.setattr(
        ollama_chat_client.urllib.request,
        "urlopen",
        fake_urlopen,
    )

    result = ollama_chat_client.ask_ollama(
        "Explain diversification.",
        context=(
            "SYSTEM ROLE\n"
            "Reference only.\n\n"
            "CURRENT USER MESSAGE\n"
            "This must not become the user request."
        ),
        model="neuro-reason:latest",
    )

    payload = json.loads(
        captured["request"].data.decode("utf-8")
    )

    system_message = payload["messages"][0]["content"]
    user_message = payload["messages"][1]["content"]

    assert result == "qualified reply"
    assert payload["model"] == "neuro-reason:latest"
    assert "CONVERSATION CONTEXT — REFERENCE ONLY" in system_message
    assert "SYSTEM ROLE" in system_message
    assert "CURRENT USER MESSAGE" in system_message
    assert "Explain diversification." in user_message
    assert "SYSTEM ROLE" not in user_message
    assert "CURRENT USER MESSAGE" not in user_message
