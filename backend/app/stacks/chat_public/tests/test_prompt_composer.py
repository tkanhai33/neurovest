from __future__ import annotations

import pytest

from backend.app.stacks.chat_public.prompt_composer import (
    PromptComposition,
    compose_prompt,
)


def identity_bounder(
    text: str,
    limit: int,
) -> str:
    return text[:limit]


def legacy_style_bounder(
    text: str,
    limit: int,
) -> str:
    if len(text) <= limit:
        return text

    return text[:limit]


def test_composer_preserves_existing_section_delimiter() -> None:
    result = compose_prompt(
        [
            "SYSTEM ROLE\nRole text",
            "TRUTH BOUNDARY\nTruth text",
            "CURRENT USER MESSAGE\nHello",
        ],
        max_characters=1000,
        bounder=identity_bounder,
    )

    assert result.prompt == (
        "SYSTEM ROLE\nRole text"
        "\n\n"
        "TRUTH BOUNDARY\nTruth text"
        "\n\n"
        "CURRENT USER MESSAGE\nHello"
    )

    assert result.section_count == 3
    assert result.truncated is False


def test_composer_uses_supplied_existing_bounder() -> None:
    calls: list[tuple[str, int]] = []

    def recording_bounder(
        text: str,
        limit: int,
    ) -> str:
        calls.append(
            (
                text,
                limit,
            )
        )

        return f"bounded:{text}"

    result = compose_prompt(
        [
            "one",
            "two",
        ],
        max_characters=321,
        bounder=recording_bounder,
    )

    assert calls == [
        (
            "one\n\ntwo",
            321,
        )
    ]

    assert result.prompt == "bounded:one\n\ntwo"


def test_composer_reports_character_metadata() -> None:
    result = compose_prompt(
        [
            "12345",
            "67890",
        ],
        max_characters=8,
        bounder=legacy_style_bounder,
    )

    assert result.unbounded_character_count == len(
        "12345\n\n67890"
    )

    assert result.final_character_count == 8
    assert result.truncated is True


def test_composer_materializes_iterables_once() -> None:
    values = (
        value
        for value in (
            "alpha",
            "beta",
            "gamma",
        )
    )

    result = compose_prompt(
        values,
        max_characters=100,
        bounder=identity_bounder,
    )

    assert result.section_count == 3
    assert result.prompt == "alpha\n\nbeta\n\ngamma"


def test_composer_rejects_invalid_limit() -> None:
    with pytest.raises(
        ValueError,
        match="max_characters must be positive",
    ):
        compose_prompt(
            ["section"],
            max_characters=0,
            bounder=identity_bounder,
        )


def test_composer_rejects_non_string_bounder_result() -> None:
    def invalid_bounder(
        text: str,
        limit: int,
    ) -> str:
        return None  # type: ignore[return-value]

    with pytest.raises(
        TypeError,
        match="bounder must return a string",
    ):
        compose_prompt(
            ["section"],
            max_characters=100,
            bounder=invalid_bounder,
        )


def test_prompt_composition_is_immutable() -> None:
    result = PromptComposition(
        prompt="test",
        section_count=1,
        unbounded_character_count=4,
        final_character_count=4,
        truncated=False,
    )

    with pytest.raises(AttributeError):
        result.prompt = "changed"  # type: ignore[misc]
