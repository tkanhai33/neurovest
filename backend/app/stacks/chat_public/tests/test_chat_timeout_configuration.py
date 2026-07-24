from __future__ import annotations

import importlib

from backend.app.stacks.chat_public import (
    ollama_chat_client,
    public_controls,
)


def test_default_timeout_alignment(
    monkeypatch,
) -> None:
    monkeypatch.delenv(
        "NEUROVEST_PUBLIC_CHAT_TIMEOUT_SECONDS",
        raising=False,
    )

    monkeypatch.delenv(
        "NEUROVEST_OLLAMA_TIMEOUT_SECONDS",
        raising=False,
    )

    reloaded_ollama = importlib.reload(
        ollama_chat_client
    )

    reloaded_controls = importlib.reload(
        public_controls
    )

    assert (
        reloaded_ollama.OLLAMA_TIMEOUT_SECONDS
        == 180.0
    )

    assert (
        reloaded_controls.DEFAULT_TIMEOUT_SECONDS
        == 210.0
    )

    assert (
        reloaded_controls.DEFAULT_TIMEOUT_SECONDS
        > reloaded_ollama.OLLAMA_TIMEOUT_SECONDS
    )


def test_timeout_environment_overrides(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "NEUROVEST_PUBLIC_CHAT_TIMEOUT_SECONDS",
        "240",
    )

    monkeypatch.setenv(
        "NEUROVEST_OLLAMA_TIMEOUT_SECONDS",
        "200",
    )

    reloaded_ollama = importlib.reload(
        ollama_chat_client
    )

    reloaded_controls = importlib.reload(
        public_controls
    )

    assert (
        reloaded_ollama.OLLAMA_TIMEOUT_SECONDS
        == 200.0
    )

    assert (
        reloaded_controls.DEFAULT_TIMEOUT_SECONDS
        == 240.0
    )

    assert (
        reloaded_controls.DEFAULT_TIMEOUT_SECONDS
        > reloaded_ollama.OLLAMA_TIMEOUT_SECONDS
    )
