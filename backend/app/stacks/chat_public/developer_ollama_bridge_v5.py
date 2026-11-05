"""Local Ollama adapter for isolated V5 developer synthesis.

Not connected to the HTTP chat route.

Authorization is enforced by the calling synthesis engine.
This adapter only provides bounded local model inference.
"""
from __future__ import annotations

import asyncio
from urllib.parse import urlsplit

from backend.app.stacks.chat_public import (
    ollama_chat_client as _client,
)


class UnsafeModelEndpoint(RuntimeError):
    pass


def require_local_endpoint(url):
    """Disallow outbound developer evidence transmission."""
    if not isinstance(url, str):
        raise UnsafeModelEndpoint("Invalid Ollama endpoint")

    try:
        parsed = urlsplit(url)
        host = (parsed.hostname or "").lower()
    except ValueError as exc:
        raise UnsafeModelEndpoint(
            "Invalid Ollama endpoint"
        ) from exc

    if (
        parsed.scheme != "http"
        or host not in (
            "127.0.0.1",
            "localhost",
            "::1",
        )
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise UnsafeModelEndpoint(
            "V5 developer inference requires loopback Ollama"
        )

    return True


def make_local_model(*, timeout=45.0, model=None):
    """Return an async callback for the existing V5 synthesizer."""
    timeout = float(timeout)

    if not 1.0 <= timeout <= 120.0:
        raise ValueError("Timeout outside supported range")

    # Refuse a remote configured Ollama endpoint.
    require_local_endpoint(_client.OLLAMA_URL)

    async def complete(prompt):
        if not isinstance(prompt, str):
            raise ValueError("Model prompt must be text")

        if not 1 <= len(prompt) <= 16000:
            raise ValueError("Model prompt outside limits")

        # Check again immediately before model invocation.
        require_local_endpoint(_client.OLLAMA_URL)

        result = await asyncio.wait_for(
            asyncio.to_thread(
                _client.ask_ollama,
                prompt,
                intent="general_conversation",
                model=model,
            ),
            timeout=timeout,
        )

        if not isinstance(result, str):
            raise TypeError("Ollama returned non-text response")

        return result

    return complete
