"""Verify internal diagnostics stay outside public SSE metadata."""

import ast
from pathlib import Path

from backend.app.stacks.chat_public.chat_api import (
    _public_chat_message_metadata,
)


def test_removes_internal_verification():
    original = {
        "response_type": "assistant",
        "response_verification": {
            "original_response": "INTERNAL_ORIGINAL_SENTINEL",
            "final_response": "INTERNAL_FINAL_SENTINEL",
            "metadata": {
                "capability_consistency_audit": {
                    "review_required": True,
                }
            },
        },
    }

    public = _public_chat_message_metadata(original)

    assert "response_verification" not in public
    assert public["response_type"] == "assistant"
    assert "response_verification" in original
    assert "INTERNAL_ORIGINAL_SENTINEL" not in str(public)
    assert "INTERNAL_FINAL_SENTINEL" not in str(public)


def test_preserves_other_metadata():
    original = {
        "response_type": "text",
        "runtime_status": "ok",
        "client_message_id": "example-id",
        "cognitive_route": {"tier": "fast"},
    }

    public = _public_chat_message_metadata(original)

    assert public == original
    assert public is not original


def test_handles_missing_metadata():
    assert _public_chat_message_metadata(None) == {}
    assert _public_chat_message_metadata({}) == {}


def test_sse_uses_filtered_metadata():
    source = (
        Path(__file__).resolve().parents[1] / "chat_api.py"
    ).read_text(encoding="utf-8")

    tree = ast.parse(source)

    handlers = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "authenticated_chat_events"
    ]

    assert len(handlers) == 1

    handler_source = ast.get_source_segment(source, handlers[0])

    assert handler_source is not None
    assert (
        '"metadata": _public_chat_message_metadata(item.metadata)'
        in handler_source
    )
    assert '"metadata": item.metadata' not in handler_source
