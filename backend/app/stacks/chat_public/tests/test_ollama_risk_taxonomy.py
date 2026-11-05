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


def test_risk_taxonomy_reaches_ollama(monkeypatch) -> None:
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
        "What risks remain in two unnamed Canadian bank stocks?",
        model="neuro-reason:latest",
    )

    payload = json.loads(captured["request"].data.decode("utf-8"))
    system_message = payload["messages"][0]["content"]

    assert "RISK ANALYSIS QUALITY" in system_message
    assert "financial-sector concentration" in system_message
    assert "Canada-specific regulatory or geographic concentration" in system_message
    assert "Do not introduce liquidity risk" in system_message
