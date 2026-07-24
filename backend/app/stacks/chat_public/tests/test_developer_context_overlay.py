from __future__ import annotations

from backend.app.stacks.chat_public.context.context_assembler import (
    _build_intent_overlay,
)


def section_map(
    metadata: dict[str, object],
) -> dict[str, str]:
    return dict(
        _build_intent_overlay(
            metadata
        )
    )


def test_general_conversation_does_not_load_developer_overlay() -> None:
    sections = section_map(
        {
            "family": "GENERAL",
            "subtype": "greeting",
            "developer_mode": False,
        }
    )

    assert "CONVERSATION CLASSIFICATION" in sections
    assert "DEVELOPER MODE" not in sections
    assert "SELF-REFLECTION MODE" not in sections
    assert "REPOSITORY SNAPSHOT" not in sections
    assert "ARCHITECTURE HEALTH" not in sections


def test_self_evaluation_adds_grounded_developer_requirements() -> None:
    sections = section_map(
        {
            "family": "DEVELOPER",
            "subtype": "self_evaluation",
            "developer_mode": True,
            "self_evaluation": True,
            "requires_repo_context": False,
            "requires_architecture_context": False,
        }
    )

    assert "DEVELOPER MODE" in sections
    assert "SELF-REFLECTION MODE" in sections
    assert "DEVELOPER RESPONSE FORMAT" in sections

    self_reflection = sections[
        "SELF-REFLECTION MODE"
    ].lower()

    assert "software self-evaluation" in self_reflection
    assert "do not describe emotions" in self_reflection
    assert "unknowns" in self_reflection


def test_architecture_mode_adds_architecture_review_rules() -> None:
    sections = section_map(
        {
            "family": "DEVELOPER",
            "subtype": "architecture_review",
            "developer_mode": True,
            "architecture_mode": True,
            "requires_repo_context": False,
            "requires_architecture_context": False,
        }
    )

    assert "ARCHITECTURE REVIEW MODE" in sections

    text = sections[
        "ARCHITECTURE REVIEW MODE"
    ].lower()

    assert "do not invent files" in text
    assert "minimal repair" in text


def test_developer_repo_and_architecture_context_are_bounded() -> None:
    sections = section_map(
        {
            "family": "DEVELOPER",
            "subtype": "self_evaluation",
            "developer_mode": True,
            "self_evaluation": True,
            "requires_repo_context": True,
            "requires_architecture_context": True,
        }
    )

    assert "REPOSITORY SNAPSHOT" in sections
    assert "DEPENDENCY GRAPH SUMMARY" in sections
    assert "REPOSITORY HOTSPOTS" in sections
    assert "COMPONENT SUMMARY" in sections
    assert "COMPONENT HOTSPOTS" in sections
    assert "ARCHITECTURE HEALTH" in sections

    assert len(
        sections[
            "REPOSITORY SNAPSHOT"
        ]
    ) <= 1800

    assert len(
        sections[
            "ARCHITECTURE HEALTH"
        ]
    ) <= 2600
