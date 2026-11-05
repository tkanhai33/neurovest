
"""Review-to-proposal integration regression tests."""

import ast
import difflib
import runpy
from pathlib import Path

import pytest

ROOT = Path.home() / "Neurovest"
BASE = ROOT / "backend/app/stacks/chat_public"

CHAT = runpy.run_path(
    str(BASE / "developer_chat_commands.py")
)
GENERATOR = runpy.run_path(
    str(ROOT / "scripts/neuro_developer_patch_preview.py")
)
APPLIER = runpy.run_path(
    str(ROOT / "scripts/neuro_developer_patch_apply.py")
)
GUARD = runpy.run_path(
    str(ROOT / "scripts/neuro_developer_patch_scope.py")
)

RELATIVE = (
    "backend/app/stacks/chat_public/"
    "developer_self_review.py"
)

parse = CHAT["parse_developer_command"]
build = GENERATOR["build_review_docstring_proposal"]
validate = GENERATOR["validate_patch"]
scope_check = GUARD["enforce_patch_scope"]



def undocumented_render_review_source():
    """Produce an in-memory, undocumented historical test fixture."""
    source = (ROOT / RELATIVE).read_text("utf-8")
    tree = ast.parse(source)

    functions = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "render_review"
    ]

    if len(functions) != 1:
        raise AssertionError("render_review anchor changed")

    function = functions[0]

    if ast.get_docstring(function) is None:
        return source

    statement = function.body[0]
    lines = source.splitlines(keepends=True)

    del lines[
        statement.lineno - 1:statement.end_lineno
    ]

    candidate = "".join(lines)
    ast.parse(candidate)

    return candidate


def test_review_finding_becomes_scoped_command():
    command = parse(
        "/dev propose-review developer_self_review render_review"
    )

    assert command[0] == "propose"
    assert command[1] == RELATIVE
    assert command[2].startswith(
        "AUTO_REVIEW_DOCSTRING:render_review"
    )


def test_unapproved_module_is_rejected():
    command = parse(
        "/dev propose-review identity_auth login"
    )
    assert command[0] == "error"


def test_invalid_function_name_is_rejected():
    command = parse(
        "/dev propose-review developer_self_review ../bad"
    )
    assert command[0] == "error"


def test_render_review_docstring_proposal():
    source = undocumented_render_review_source()
    task = parse(
        "/dev propose-review developer_self_review render_review"
    )[2]

    proposal = build(source, "render_review")
    candidate = validate(source, proposal)

    tree = ast.parse(candidate)

    function = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "render_review"
    )

    assert ast.get_docstring(function)
    assert scope_check(
        source, candidate, task
    ) == "TARGET_FUNCTION_DOCSTRING_ONLY"


def test_applier_accepts_review_proposal_diff():
    source = undocumented_render_review_source()
    candidate = validate(
        source,
        build(source, "render_review"),
    )

    diff = "".join(difflib.unified_diff(
        source.splitlines(keepends=True),
        candidate.splitlines(keepends=True),
        fromfile="a/" + RELATIVE,
        tofile="b/" + RELATIVE,
    ))

    assert APPLIER["apply_unified_diff"](
        source, diff, RELATIVE
    ) == candidate


def test_existing_docstring_cannot_be_regenerated():
    source = (
        "def existing():\n"
        '    """Already documented."""\n'
        "    return 1\n"
    )

    with pytest.raises(ValueError, match="already has"):
        build(source, "existing")


def test_wrong_function_cannot_be_generated():
    source = (ROOT / RELATIVE).read_text("utf-8")

    with pytest.raises(ValueError, match="not found"):
        build(source, "not_a_real_function")


def test_unscoped_general_proposals_still_supported():
    command = parse(
        "/dev propose "
        + RELATIVE
        + " :: Improve the function inventory safely"
    )

    assert command[0] == "propose"


def test_approval_still_requires_explicit_consent():
    proposal = "proposal_20261012_110156_349662_4051636"

    assert parse(
        "/dev apply " + proposal
    )[0] == "error"

    assert parse(
        "/dev apply " + proposal + " --approve"
    ) == ("apply", proposal)
