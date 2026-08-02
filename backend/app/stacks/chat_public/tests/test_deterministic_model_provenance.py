from __future__ import annotations

from unittest.mock import patch

from backend.app.stacks.chat_public.chat_runtime import (
    handle_chat_message,
)
from backend.app.stacks.chat_public.ollama_chat_client import (
    resolve_runtime_model,
)


def test_runtime_model_resolver_preserves_none() -> None:
    assert resolve_runtime_model(None) is None


def test_runtime_model_resolver_preserves_explicit_model() -> None:
    assert (
        resolve_runtime_model(
            "qualified-test-model"
        )
        == "qualified-test-model"
    )


def test_runtime_model_resolver_applies_known_alias() -> None:
    assert (
        resolve_runtime_model(
            "neuro-reason:latest"
        )
        is not None
    )


def test_developer_capability_response_has_no_model() -> None:
    with patch(
        "backend.app.stacks.chat_public.chat_runtime.ask_ollama"
    ) as mocked_ollama:
        result = handle_chat_message(
            "As your developer, what capabilities "
            "are currently available?",
            developer_evidence_allowed=True,
        )

    mocked_ollama.assert_not_called()

    assert result["status"] == "ok"
    assert result["provider"] == "neurovest_local_evidence"
    assert result["model"] is None
    assert result["tool_truth_state"] == "grounded"


def test_developer_improvement_response_has_no_model() -> None:
    with patch(
        "backend.app.stacks.chat_public.chat_runtime.ask_ollama"
    ) as mocked_ollama:
        result = handle_chat_message(
            "As your developer, how can I help you improve?",
            developer_evidence_allowed=True,
        )

    mocked_ollama.assert_not_called()

    assert result["status"] == "ok"
    assert result["provider"] == "neurovest_local_evidence"
    assert result["model"] is None


def test_model_backed_response_keeps_model_provenance() -> None:
    with patch(
        "backend.app.stacks.chat_public.chat_runtime.ask_ollama",
        return_value="Model response.",
    ) as mocked_ollama:
        result = handle_chat_message(
            "Explain portfolio diversification.",
            developer_evidence_allowed=False,
        )

    mocked_ollama.assert_called()

    assert result["provider"] != "neurovest_local_evidence"
    assert result["model"] is not None
