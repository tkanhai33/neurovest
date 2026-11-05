from __future__ import annotations

from backend.app.stacks.chat_public.chat_system_prompt import (
    SYSTEM_PROMPT,
)


def normalized_prompt() -> str:
    return " ".join(
        SYSTEM_PROMPT.lower().split()
    )


def test_prompt_requires_direct_completion() -> None:
    prompt = normalized_prompt()

    assert (
        "complete a sufficiently specified request directly"
        in prompt
    )

    assert (
        "do not replace a clear request with unnecessary "
        "clarifying questions"
        in prompt
    )


def test_prompt_requires_explicit_count_completion() -> None:
    prompt = normalized_prompt()

    assert (
        "exact number of items, steps, sections, or examples"
        in prompt
    )

    assert (
        "provide at least that number"
        in prompt
    )


def test_prompt_requires_every_requested_component() -> None:
    prompt = normalized_prompt()

    assert (
        "address every requested component"
        in prompt
    )

    assert (
        "before offering optional follow-up questions"
        in prompt
    )

    assert (
        "requested component has been omitted"
        in prompt
    )


def test_prompt_requires_generic_factual_honesty() -> None:
    prompt = normalized_prompt()

    required = (
        "do not invent facts",
        "commands",
        "procedures",
        "calculations",
        "citations",
        "repository paths",
        "results",
        "capabilities",
        "completed actions",
        "state uncertainty",
        "rather than guessing",
    )

    for marker in required:
        assert marker in prompt


def test_prompt_contains_no_aiq_domain_contamination() -> None:
    prompt = normalized_prompt()

    forbidden = (
        "fixture-unit demand",
        "bathroom count",
        "water-service inputs",
        "keyboard shortcuts",
        "for plumbing",
        "for blender",
        "for software and modelling guidance",
    )

    for marker in forbidden:
        assert marker not in prompt


def test_prompt_does_not_modify_execution_policy() -> None:
    prompt = normalized_prompt()

    required_policy = (
        "live trading: disabled",
        "production broker execution: disabled",
        "execute live trades",
        "place real trades",
        "modify live brokerage orders",
        "cancel live brokerage orders",
        "live execution remains locked",
    )

    for marker in required_policy:
        assert marker in prompt
