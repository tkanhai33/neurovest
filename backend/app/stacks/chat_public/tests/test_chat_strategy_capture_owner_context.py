from types import SimpleNamespace

from backend.app.stacks.chat_public import chat_runtime


def test_legacy_runtime_without_principal_skips_owner_capture(
    monkeypatch,
) -> None:
    def fail_capture(*_args, **_kwargs):
        raise AssertionError(
            "Owner-scoped capture must not run without an owner."
        )

    monkeypatch.setattr(
        chat_runtime,
        "ask_ollama",
        lambda *_args, **_kwargs: "Hello.",
    )
    monkeypatch.setattr(
        chat_runtime,
        "capture_strategy_proposal",
        fail_capture,
    )

    result = chat_runtime.handle_chat_message(
        "Hello there.",
    )

    assert result["strategy_capture"] is None


def test_authenticated_runtime_passes_owner_to_capture(
    monkeypatch,
) -> None:
    captured = {}

    def record_capture(*_args, **kwargs):
        captured.update(kwargs)
        return None

    monkeypatch.setattr(
        chat_runtime,
        "ask_ollama",
        lambda *_args, **_kwargs: "Hello.",
    )
    monkeypatch.setattr(
        chat_runtime,
        "capture_strategy_proposal",
        record_capture,
    )

    result = chat_runtime.handle_chat_message(
        "Hello there.",
        principal=SimpleNamespace(subject="owner-qualification"),
    )

    assert result["strategy_capture"] is None
    assert captured["owner_user_id"] == "owner-qualification"
