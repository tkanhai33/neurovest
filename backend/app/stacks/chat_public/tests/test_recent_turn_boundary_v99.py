from backend.app.stacks.chat_public.context import (
    context_assembler as ca,
)


def test_v99_short_history_unchanged():
    history = "USER: Hello\nASSISTANT: Hi"
    assert ca._retain_recent_turns_v99(history, 200) == history


def test_v99_keeps_newest_complete_messages():
    history = (
        "USER: " + "old topic " * 800
        + "\nASSISTANT: Old answer."
        + "\nUSER: Use the blue design."
        + "\nASSISTANT: Blue selected."
        + "\nUSER: What did we settle on?"
    )

    result = ca._retain_recent_turns_v99(history, 250)

    assert result.startswith(
        "[Earlier dialogue omitted to fit context.]\n"
    )
    assert "USER: Use the blue design." in result
    assert "ASSISTANT: Blue selected." in result
    assert "USER: What did we settle on?" in result
    assert "old topic " not in result
    assert len(result) <= 250


def test_v99_does_not_begin_inside_old_message():
    history = (
        "USER: " + "unrelated history " * 600
        + "\nUSER: My computer crashes during gaming."
        + "\nASSISTANT: We discussed a power supply problem."
    )

    result = ca._retain_recent_turns_v99(history, 180)

    assert result.startswith(
        "[Earlier dialogue omitted to fit context.]\nUSER:"
    )
    assert "computer crashes during gaming" in result
    assert "power supply problem" in result
    assert len(result) <= 180


def test_v99_single_oversized_message_is_labelled():
    history = "USER: " + "details " * 1000

    result = ca._retain_recent_turns_v99(history, 240)

    assert result.startswith(
        "[Earlier dialogue omitted to fit context.]\nUSER: "
    )
    assert "[message truncated]" in result
    assert len(result) <= 240


def test_v99_real_prompt_composer_retains_recent_context():
    history = (
        "USER: " + "unrelated " * 1500
        + "\nUSER: We're building a Rust CLI."
        + "\nASSISTANT: Yes, the project uses Rust."
    )

    sections = [
        "SYSTEM ROLE\nYou are Neuro.",
        "TRUTH BOUNDARY\nNever invent tool results.",
        "THREAD SUMMARY\n" + "older " * 2500,
        "RECENT CONVERSATION\n" + history,
        "CURRENT USER MESSAGE\nWhich language were we using?",
        "RESPONSE REQUIREMENTS\nAnswer accurately.",
    ]

    result = ca._compose_chat_prompt_v95r2(
        sections,
        max_characters=14000,
    )

    assert len(result.prompt) <= 14000
    assert "USER: We're building a Rust CLI." in result.prompt
    assert "ASSISTANT: Yes, the project uses Rust." in result.prompt
    assert "Which language were we using?" in result.prompt
    assert "Never invent tool results." in result.prompt
