
from types import SimpleNamespace

from backend.app.stacks.chat_public.context.context_assembler import (
    _format_recent_messages,
    _project_assistant_history_v4r2,
)

WITHHELD = (
    "[Unverified historical capability assertion withheld.]"
)


def msg(role, content):
    return SimpleNamespace(role=role, content=content)


def test_sentence_splitting_is_real():
    content = (
        "An ETF is an exchange-traded fund. "
        "Paper trading is currently disabled. "
        "Live orders remain locked."
    )

    result = _project_assistant_history_v4r2(content)

    assert result == (
        "An ETF is an exchange-traded fund. "
        + WITHHELD
        + " Live orders remain locked."
    )


def test_disabled_by_default(monkeypatch):
    monkeypatch.delenv(
        "NEUROVEST_HISTORY_PROJECTION_V1",
        raising=False,
    )

    text = "Paper trading is currently disabled."

    assert _format_recent_messages(
        [msg("assistant", text)]
    ) == "ASSISTANT: " + text


def test_selective_projection(monkeypatch):
    monkeypatch.setenv(
        "NEUROVEST_HISTORY_PROJECTION_V1",
        "1",
    )

    original = (
        "An ETF is an exchange-traded fund. "
        "As for simulated paper trades — they’re currently disabled. "
        "Live brokerage orders remain locked. "
        "Personal training stays owner-scoped."
    )

    message = msg("assistant", original)
    result = _format_recent_messages([message])

    assert "An ETF is an exchange-traded fund." in result
    assert "Live brokerage orders remain locked." in result
    assert "Personal training stays owner-scoped." in result
    assert "they’re currently disabled" not in result
    assert result.count(WITHHELD) == 1
    assert message.content == original


def test_two_false_claims_and_safe_context(monkeypatch):
    monkeypatch.setenv(
        "NEUROVEST_HISTORY_PROJECTION_V1",
        "1",
    )

    content = (
        "Personal training stays owner-scoped. "
        "Paper trading is currently disabled. "
        "An ETF is an exchange-traded fund. "
        "Simulated paper trades — they're currently disabled. "
        "Real brokerage orders remain locked."
    )

    result = _format_recent_messages(
        [msg("assistant", content)]
    )

    assert result.count(WITHHELD) == 2
    assert "Personal training stays owner-scoped." in result
    assert "An ETF is an exchange-traded fund." in result
    assert "Real brokerage orders remain locked." in result


def test_user_history_unchanged(monkeypatch):
    monkeypatch.setenv(
        "NEUROVEST_HISTORY_PROJECTION_V1",
        "1",
    )

    text = "I think paper trading is currently disabled."

    assert _format_recent_messages(
        [msg("user", text)]
    ) == "USER: " + text


def test_correction_preserved(monkeypatch):
    monkeypatch.setenv(
        "NEUROVEST_HISTORY_PROJECTION_V1",
        "1",
    )

    text = (
        "The earlier statement that paper trading "
        "is disabled was incorrect."
    )

    assert text in _format_recent_messages(
        [msg("assistant", text)]
    )


def test_reported_question_preserved(monkeypatch):
    monkeypatch.setenv(
        "NEUROVEST_HISTORY_PROJECTION_V1",
        "1",
    )

    text = (
        "They wanted to know whether simulations "
        "are disabled."
    )

    assert text in _format_recent_messages(
        [msg("assistant", text)]
    )


def test_ordinary_conversation_unchanged(monkeypatch):
    monkeypatch.setenv(
        "NEUROVEST_HISTORY_PROJECTION_V1",
        "1",
    )

    messages = [
        msg("user", "What is an ETF?"),
        msg(
            "assistant",
            "An ETF is an exchange-traded fund.",
        ),
    ]

    result = _format_recent_messages(messages)

    assert result == (
        "USER: What is an ETF?\n"
        "ASSISTANT: An ETF is an exchange-traded fund."
    )


def test_other_flag_values_remain_disabled(monkeypatch):
    text = "Paper trading is currently disabled."

    for value in ("false", "0", "yes", ""):
        monkeypatch.setenv(
            "NEUROVEST_HISTORY_PROJECTION_V1",
            value,
        )

        assert text in _format_recent_messages(
            [msg("assistant", text)]
        )


def test_multiple_messages_preserve_order(monkeypatch):
    monkeypatch.setenv(
        "NEUROVEST_HISTORY_PROJECTION_V1",
        "1",
    )

    messages = [
        msg("user", "Can I paper trade?"),
        msg("assistant", "Paper trading is disabled."),
        msg("user", "And what is an ETF?"),
        msg(
            "assistant",
            "An ETF is an exchange-traded fund.",
        ),
    ]

    result = _format_recent_messages(messages)

    assert result.splitlines() == [
        "USER: Can I paper trade?",
        "ASSISTANT: " + WITHHELD,
        "USER: And what is an ETF?",
        "ASSISTANT: An ETF is an exchange-traded fund.",
    ]
