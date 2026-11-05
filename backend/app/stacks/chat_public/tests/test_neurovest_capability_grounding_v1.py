"""NeuroVest V1 capability grounding contracts."""

import json

from backend.app.stacks.chat_public import ollama_chat_client
from backend.app.stacks.chat_public.neurovest_capability_grounding import (
    NEUROVEST_CAPABILITY_GROUNDING_V1,
)


def test_capability_distinctions():
    text = NEUROVEST_CAPABILITY_GROUNDING_V1

    for phrase in (
        "PERSONAL STRATEGY TRAINING",
        "SYSTEM-WIDE STRATEGY TRAINING",
        "MARKET DATA AND CONNECTED ACCOUNTS",
        "BROKERAGE AND SAFETY",
        "GENERAL AI CONVERSATION",
        "ANSWER QUALITY",
    ):
        assert phrase in text


def test_training_is_not_model_weight_learning():
    text = NEUROVEST_CAPABILITY_GROUNDING_V1

    assert "does not automatically retrain" in text
    assert "isolated from the global strategy profile" in text
    assert "independent developer" in text


def test_market_data_not_broker_execution():
    text = NEUROVEST_CAPABILITY_GROUNDING_V1

    assert "read-only connected brokerage" in text
    assert "different capabilities" in text
    assert "not permission to place an order" in text


def test_grounding_reaches_ollama_system_message(monkeypatch):
    captured = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

        def read(self):
            return json.dumps(
                {"message": {"content": "qualified reply"}}
            ).encode("utf-8")

    def fake_urlopen(request, timeout):
        captured["request"] = request
        return FakeResponse()

    monkeypatch.setattr(
        ollama_chat_client.urllib.request,
        "urlopen",
        fake_urlopen,
    )

    ollama_chat_client.ask_ollama(
        "Explain why the sky appears blue.",
        model="neuro-reason:latest",
    )

    payload = json.loads(captured["request"].data.decode("utf-8"))
    system_message = payload["messages"][0]["content"]

    assert NEUROVEST_CAPABILITY_GROUNDING_V1 in system_message



def test_grounding_is_explanatory_only():
    text = NEUROVEST_CAPABILITY_GROUNDING_V1

    assert "without authoritative confirmation" in text
    assert "not an entitlement" in text
