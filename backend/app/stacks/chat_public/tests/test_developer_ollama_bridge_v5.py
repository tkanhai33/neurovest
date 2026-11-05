import asyncio
import hashlib
import json
from types import SimpleNamespace

import pytest

from backend.app.stacks.chat_public import (
    developer_ollama_bridge_v5 as bridge,
)
from backend.app.stacks.chat_public import (
    developer_model_synthesis_v5 as synthesis,
)


def test_loopback_endpoint_allowed():
    for url in (
        "http://127.0.0.1:11434/api/chat",
        "http://localhost:11434/api/chat",
        "http://[::1]:11434/api/chat",
    ):
        assert bridge.require_local_endpoint(url)


@pytest.mark.parametrize("url", [
    "https://api.example.com/chat",
    "http://192.168.1.10:11434/api/chat",
    "http://example.com:11434/api/chat",
    "file:///tmp/model",
    "http://user:pass@localhost:11434/api/chat",
])
def test_remote_or_unsafe_endpoints_rejected(url):
    with pytest.raises(bridge.UnsafeModelEndpoint):
        bridge.require_local_endpoint(url)


def test_async_bridge_calls_existing_client(monkeypatch):
    observed = []

    def fake_ollama(message, *, intent, model):
        observed.append((message, intent, model))
        return "A local model response."

    monkeypatch.setattr(
        bridge,
        "_client",
        SimpleNamespace(
            OLLAMA_URL="http://127.0.0.1:11434/api/chat",
            ask_ollama=fake_ollama,
        ),
    )

    callback = bridge.make_local_model(
        timeout=5,
        model=None,
    )

    result = asyncio.run(callback("Explain source evidence"))

    assert result == "A local model response."
    assert observed == [
        (
            "Explain source evidence",
            "general_conversation",
            None,
        )
    ]


def test_bridge_timeout(monkeypatch):
    import time

    def slow_model(message, *, intent, model):
        time.sleep(0.15)
        return "Late result"

    monkeypatch.setattr(
        bridge,
        "_client",
        SimpleNamespace(
            OLLAMA_URL="http://localhost:11434/api/chat",
            ask_ollama=slow_model,
        ),
    )

    callback = bridge.make_local_model(timeout=1)

    # Verify callback remains asynchronous.
    assert asyncio.iscoroutinefunction(callback)


def test_runtime_endpoint_rechecked(monkeypatch):
    client = SimpleNamespace(
        OLLAMA_URL="http://localhost:11434/api/chat",
        ask_ollama=lambda *args, **kwargs: "OK",
    )
    monkeypatch.setattr(bridge, "_client", client)

    callback = bridge.make_local_model()
    client.OLLAMA_URL = "https://remote.example.com/api/chat"

    with pytest.raises(bridge.UnsafeModelEndpoint):
        asyncio.run(callback("Developer source evidence"))


def test_evidence_to_model_to_answer(monkeypatch, tmp_path):
    source = tmp_path / "chat_runtime.py"
    source.write_text(
        "def run_chat_turn(): pass\n",
        encoding="utf-8",
    )

    manifest = tmp_path / "index.json"
    manifest.write_text(json.dumps({
        "schema": "neurovest_v5_ast_evidence_candidate_v1",
        "status": "CANDIDATE_ONLY",
        "sources": {
            "chat_runtime.py": {
                "sha256": hashlib.sha256(
                    source.read_bytes()
                ).hexdigest(),
                "definitions": [{
                    "name": "run_chat_turn",
                    "kind": "function",
                    "line": 1,
                    "syntactic_calls": [],
                }],
            }
        },
    }), encoding="utf-8")

    calls = []

    def fake_ollama(message, *, intent, model):
        calls.append(message)
        return (
            "The function `run_chat_turn` is defined at "
            "chat_runtime.py:1. This demonstrates that "
            "the symbol exists in source; it does not "
            "prove its execution in a live request."
        )

    monkeypatch.setattr(
        bridge,
        "_client",
        SimpleNamespace(
            OLLAMA_URL="http://127.0.0.1:11434/api/chat",
            ask_ollama=fake_ollama,
        ),
    )

    monkeypatch.setattr(
        synthesis,
        "authenticated_developer_role",
        lambda principal: getattr(
            principal, "subject", None
        ) == "dev",
    )

    principal = SimpleNamespace(subject="dev")
    thread = SimpleNamespace(
        thread_id="test-thread",
        user_id="dev",
    )

    result = asyncio.run(
        synthesis.synthesize_developer_answer(
            root=tmp_path,
            index_path=manifest,
            question="Explain our chat runtime",
            principal=principal,
            thread=thread,
            model=bridge.make_local_model(),
        )
    )

    assert "run_chat_turn" in result
    assert "does not prove" in result
    assert len(calls) == 1


def test_unauthorized_does_not_call_ollama(
    monkeypatch, tmp_path,
):
    calls = []

    monkeypatch.setattr(
        synthesis,
        "authenticated_developer_role",
        lambda principal: False,
    )

    monkeypatch.setattr(
        bridge,
        "_client",
        SimpleNamespace(
            OLLAMA_URL="http://localhost:11434/api/chat",
            ask_ollama=lambda *args, **kwargs: calls.append(1),
        ),
    )

    with pytest.raises(synthesis.DeveloperAccessDenied):
        asyncio.run(
            synthesis.synthesize_developer_answer(
                root=tmp_path,
                index_path=tmp_path / "missing.json",
                question="Inspect our codebase",
                principal=SimpleNamespace(subject="normal"),
                thread=SimpleNamespace(
                    thread_id="thread",
                    user_id="normal",
                ),
                model=bridge.make_local_model(),
            )
        )

    assert calls == []
