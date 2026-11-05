from backend.app.stacks.chat_public.context import (
    context_assembler as ca,
)


def sections(summary, recent, current):
    return [
        "SYSTEM ROLE\nYou are Neuro.",
        "TRUTH BOUNDARY\nDo not invent results.",
        "THREAD SUMMARY\n" + summary,
        "REMEMBERED TERMS\n(none)",
        "ACTIVE STRATEGY\n(none)",
        "RECENT CONVERSATION\n" + recent,
        "CURRENT USER MESSAGE\n" + current,
        "RESPONSE REQUIREMENTS\nAnswer accurately.",
    ]


def test_v95r2_normal_prompt_unchanged():
    items = sections(
        "Short summary",
        "USER: Hello\nASSISTANT: Hello!",
        "How are you?",
    )
    previous = ca.compose_prompt(
        items,
        max_characters=14000,
        bounder=ca._bounded,
    )
    result = ca._compose_chat_prompt_v95r2(
        items,
        max_characters=14000,
    )
    assert result.prompt == previous.prompt
    assert not result.truncated


def test_v95r2_oversized_history_retains_current():
    items = sections(
        "OLD SUMMARY " * 2300,
        "OLD HISTORY " * 1400
        + "\nUSER: I prefer the first design.",
        "Actually, use the second design.",
    )
    result = ca._compose_chat_prompt_v95r2(
        items,
        max_characters=14000,
    )
    assert result.truncated
    assert len(result.prompt) <= 14000
    assert "SYSTEM ROLE\n" in result.prompt
    assert "Do not invent results." in result.prompt
    assert "I prefer the first design." in result.prompt
    assert "Actually, use the second design." in result.prompt
    assert "RESPONSE REQUIREMENTS\nAnswer accurately." in result.prompt


def test_v95r2_oversized_current_message():
    items = sections(
        "OLD SUMMARY " * 2300,
        "USER: We discussed Python and Rust.",
        "Compare them. " + "details " * 5000,
    )
    result = ca._compose_chat_prompt_v95r2(
        items,
        max_characters=14000,
    )
    assert len(result.prompt) <= 14000
    assert "Compare them." in result.prompt
    assert "We discussed Python and Rust." in result.prompt
    assert "Answer accurately." in result.prompt


def test_v95r2_latest_history_end_preserved():
    history = (
        "USER: Long unrelated discussion.\n" * 500
        + "USER: My computer fails during gaming.\n"
        + "ASSISTANT: We discussed a possible power issue."
    )
    result = ca._compose_chat_prompt_v95r2(
        sections(
            "Historical background " * 1500,
            history,
            "Could the power supply be responsible?",
        ),
        max_characters=14000,
    )
    assert len(result.prompt) <= 14000
    assert "My computer fails during gaming." in result.prompt
    assert "possible power issue." in result.prompt
    assert "Could the power supply be responsible?" in result.prompt
