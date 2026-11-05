"""Focused multi-edit proposal validation and diff compatibility."""

import ast
import difflib
import runpy
from pathlib import Path

import pytest

ROOT = Path.home() / "Neurovest"

PREVIEW = runpy.run_path(
    str(ROOT / "scripts/neuro_developer_patch_preview.py")
)

APPLIER = runpy.run_path(
    str(ROOT / "scripts/neuro_developer_patch_apply.py")
)

validate_patch = PREVIEW["validate_patch"]
apply_unified_diff = APPLIER["apply_unified_diff"]

RELATIVE = (
    "backend/app/stacks/chat_public/"
    "developer_repository_inspection.py"
)

ORIGINAL = (
    "def inspect_repository(query):\n"
    "    if any(term in query.lower() for term in "
    "('password=', 'token=')):\n"
    "        return ''\n"
    "    return query\n"
)

INSERT_OLD = "def inspect_repository(query):"

INSERT_NEW = (
    "def _is_sensitive_term(text):\n"
    "    return any(term in text.lower() for term in "
    "('password=', 'token='))\n"
    "\n"
    "\n"
    "def inspect_repository(query):"
)

CONDITION_OLD = (
    "if any(term in query.lower() for term in "
    "('password=', 'token=')):"
)

CONDITION_NEW = "if _is_sensitive_term(query):"


def two_edit_proposal():
    return {
        "edits": [
            {"old": INSERT_OLD, "new": INSERT_NEW},
            {"old": CONDITION_OLD, "new": CONDITION_NEW},
        ],
        "explanation": "Extract credential check.",
    }


def test_coordinated_helper_extraction():
    candidate = validate_patch(
        ORIGINAL, two_edit_proposal()
    )

    tree = ast.parse(candidate)

    names = [
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
    ]

    assert "_is_sensitive_term" in names
    assert "inspect_repository" in names
    assert CONDITION_NEW in candidate
    assert CONDITION_OLD not in candidate


def test_credential_behavior_preserved():
    candidate = validate_patch(
        ORIGINAL, two_edit_proposal()
    )

    namespace_before = {}
    namespace_after = {}

    # Synthetic local fixtures only, never repository source.
    exec(compile(ORIGINAL, "<original-fixture>", "exec"),
         namespace_before)
    exec(compile(candidate, "<candidate-fixture>", "exec"),
         namespace_after)

    for query in (
        "hello",
        "PASSWORD=example",
        "token=example",
        "ordinary search",
        "Bearer something",
        "",
    ):
        assert (
            namespace_before["inspect_repository"](query)
            == namespace_after["inspect_repository"](query)
        )


def test_undefined_helper_rejected():
    with pytest.raises(
        ValueError, match="Undefined _is_sensitive_term"
    ):
        validate_patch(
            ORIGINAL,
            {
                "edits": [{
                    "old": CONDITION_OLD,
                    "new": CONDITION_NEW,
                }],
            },
        )


def test_overlapping_edits_rejected():
    with pytest.raises(ValueError, match="Overlapping"):
        validate_patch(
            ORIGINAL,
            {
                "edits": [
                    {
                        "old": "return query",
                        "new": "return query.strip()",
                    },
                    {
                        "old": "query\n",
                        "new": "query\n# extra\n",
                    },
                ],
            },
        )


def test_ambiguous_source_rejected():
    with pytest.raises(ValueError, match="exact source match"):
        validate_patch(
            "return 1\nreturn 1\n",
            {
                "edits": [{
                    "old": "return 1",
                    "new": "return 2",
                }],
            },
        )


def test_invalid_python_rejected():
    with pytest.raises(SyntaxError):
        validate_patch(
            ORIGINAL,
            {
                "edits": [{
                    "old": "return query",
                    "new": "return (query",
                }],
            },
        )


def test_too_many_edits_rejected():
    with pytest.raises(ValueError, match="1–4"):
        validate_patch(
            ORIGINAL,
            {"edits": [
                {"old": "a", "new": "b"}
                for _ in range(5)
            ]},
        )


def test_legacy_single_edit_remains_supported():
    result = validate_patch(
        ORIGINAL,
        {
            "old": "return query",
            "new": "return query.strip()",
        },
    )

    assert "return query.strip()" in result


def test_mixed_formats_rejected():
    with pytest.raises(ValueError, match="Mixed"):
        validate_patch(
            ORIGINAL,
            {
                "old": "return query",
                "new": "return query.strip()",
                "edits": [],
            },
        )


def test_multiple_hunks_supported_by_existing_applier():
    original = (
        "def first():\n"
        "    return 1\n"
        + "".join(
            f"# filler {i}\n" for i in range(15)
        )
        + "def last():\n"
        "    return 2\n"
    )

    proposal = {
        "edits": [
            {"old": "return 1", "new": "return 10"},
            {"old": "return 2", "new": "return 20"},
        ],
    }

    candidate = validate_patch(original, proposal)

    diff = "".join(difflib.unified_diff(
        original.splitlines(keepends=True),
        candidate.splitlines(keepends=True),
        fromfile="a/" + RELATIVE,
        tofile="b/" + RELATIVE,
    ))

    assert diff.count("@@ -") >= 2

    reconstructed = apply_unified_diff(
        original, diff, RELATIVE
    )

    assert reconstructed == candidate
