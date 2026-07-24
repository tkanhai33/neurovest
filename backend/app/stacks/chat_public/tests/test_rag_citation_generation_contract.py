from __future__ import annotations

from backend.app.stacks.chat_public.chat_runtime import (
    _ensure_approved_retrieval_citation,
)


def citations() -> tuple[dict[str, str], ...]:
    return (
        {
            "citation":
                "[chunk_approved_first]",
        },
        {
            "citation":
                "[chunk_approved_second]",
        },
    )


def test_missing_approved_citation_is_appended() -> None:
    result = _ensure_approved_retrieval_citation(
        "The model generated a grounded explanation.",
        citations(),
    )

    assert (
        "[chunk_approved_first]"
        in result
    )

    assert (
        "Approved local research source:"
        in result
    )


def test_existing_approved_citation_is_preserved() -> None:
    original = (
        "The grounded claim is supported here "
        "[chunk_approved_second]."
    )

    result = _ensure_approved_retrieval_citation(
        original,
        citations(),
    )

    assert result == original


def test_numeric_reference_does_not_satisfy_contract() -> None:
    result = _ensure_approved_retrieval_citation(
        "The model used an ordinary reference [1].",
        citations(),
    )

    assert "[1]" in result

    assert (
        "[chunk_approved_first]"
        in result
    )


def test_empty_citation_set_does_not_modify_response() -> None:
    original = "No retrieval evidence was available."

    result = _ensure_approved_retrieval_citation(
        original,
        (),
    )

    assert result == original
