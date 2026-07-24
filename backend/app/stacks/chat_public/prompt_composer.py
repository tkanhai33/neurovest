from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass


PromptBounder = Callable[[str, int], str]


@dataclass(frozen=True)
class PromptComposition:
    """
    Result of composing ordered prompt sections.

    Stage 4B intentionally preserves the existing prompt text and ordering.
    Role and subscription overlays are added only in later Stage 4 work.
    """

    prompt: str
    section_count: int
    unbounded_character_count: int
    final_character_count: int
    truncated: bool


def compose_prompt(
    sections: Iterable[str],
    *,
    max_characters: int,
    bounder: PromptBounder,
) -> PromptComposition:
    """
    Compose an ordered prompt using the existing Neuro delimiter and bounder.

    This boundary performs no authorization, capability probing, model call,
    persistence, external I/O, broker action, or repository mutation.
    """

    if max_characters <= 0:
        raise ValueError(
            "max_characters must be positive"
        )

    normalized_sections = tuple(
        str(section)
        for section in sections
    )

    unbounded_prompt = "\n\n".join(
        normalized_sections
    )

    final_prompt = bounder(
        unbounded_prompt,
        max_characters,
    )

    if not isinstance(final_prompt, str):
        raise TypeError(
            "bounder must return a string"
        )

    return PromptComposition(
        prompt=final_prompt,
        section_count=len(normalized_sections),
        unbounded_character_count=len(
            unbounded_prompt
        ),
        final_character_count=len(
            final_prompt
        ),
        truncated=(
            final_prompt != unbounded_prompt
        ),
    )


__all__ = [
    "PromptBounder",
    "PromptComposition",
    "compose_prompt",
]
