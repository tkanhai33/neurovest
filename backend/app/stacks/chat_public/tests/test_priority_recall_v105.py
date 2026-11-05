from backend.app.stacks.chat_public.context import (
    context_assembler as ca,
)


def make_sections(
    *,
    summary_size=0,
    memory_size=0,
    recent=None,
    current=None,
):
    older_fact = (
        "USER: We chose Rust for the command-line project.\n"
        "ASSISTANT: Rust was the selected language."
    )

    if recent is None:
        recent = (
            "USER: Our website theme was red.\n"
            "ASSISTANT: Understood.\n"
            "USER: Actually switch the website theme to blue.\n"
            "ASSISTANT: Blue replaces red."
        )

    if current is None:
        current = (
            "Back to our programming project, "
            "which language did we choose?"
        )

    return [
        "SYSTEM ROLE\nYou are Neuro.",
        "TRUTH BOUNDARY\nNever invent permissions.",
        (
            "AUTHORIZED ROLE OVERLAY\n"
            "V105_ROLE_OVERLAY"
        ),
        "THREAD SUMMARY\n" + "historical " * summary_size,
        "REMEMBERED TERMS\n" + "remembered " * memory_size,
        "DURABLE MEMORY FACTS\n" + "memory " * memory_size,
        "RELEVANT EARLIER CONVERSATION\n" + older_fact,
        "RECENT CONVERSATION\n" + recent,
        "CURRENT USER MESSAGE\n" + current,
        "RESPONSE REQUIREMENTS\nAnswer accurately.",
    ]


def test_v105_forced_overflow_recall():
    sections = make_sections(
        summary_size=2500,
        memory_size=1200,
    )

    assert len("\n\n".join(sections)) > 14000

    result = ca._compose_chat_prompt_v95r2(
        sections,
        max_characters=14000,
    )

    assert result.truncated
    assert len(result.prompt) <= 14000
    assert "We chose Rust for the command-line project." in result.prompt
    assert "Rust was the selected language." in result.prompt
    assert "Actually switch the website theme to blue." in result.prompt
    assert "V105_ROLE_OVERLAY" in result.prompt
    assert "Never invent permissions." in result.prompt
    assert "which language did we choose?" in result.prompt
    assert "RESPONSE REQUIREMENTS\nAnswer accurately." in result.prompt


def test_v105_short_prompt_is_unchanged():
    sections = make_sections()

    original = ca.compose_prompt(
        sections,
        max_characters=14000,
        bounder=ca._bounded,
    )

    result = ca._compose_chat_prompt_v95r2(
        sections,
        max_characters=14000,
    )

    assert not result.truncated
    assert original.prompt == result.prompt


def test_v105_recent_correction_survives_long_history():
    recent = (
        "USER: " + "unrelated context " * 900
        + "\nUSER: Actually use the blue design."
        + "\nASSISTANT: Blue replaces the earlier design."
    )

    result = ca._compose_chat_prompt_v95r2(
        make_sections(
            summary_size=2000,
            recent=recent,
        ),
        max_characters=14000,
    )

    assert "Actually use the blue design." in result.prompt
    assert "Blue replaces the earlier design." in result.prompt
    assert "We chose Rust" in result.prompt
    assert len(result.prompt) <= 14000


def test_v105_large_current_message_is_bounded():
    result = ca._compose_chat_prompt_v95r2(
        make_sections(
            summary_size=2000,
            current="Explain Rust. " + "details " * 3000,
        ),
        max_characters=14000,
    )

    assert "Explain Rust." in result.prompt
    assert "Never invent permissions." in result.prompt
    assert "V105_ROLE_OVERLAY" in result.prompt
    assert "We chose Rust" in result.prompt
    assert len(result.prompt) <= 14000
