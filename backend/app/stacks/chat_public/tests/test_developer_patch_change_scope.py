
"""Tests for NeuroVest's AST change-scope guard."""

import ast
import runpy
from pathlib import Path

import pytest

ROOT = Path.home() / "Neurovest"

guard = runpy.run_path(
    str(ROOT / "scripts/neuro_developer_patch_scope.py")
)
enforce = guard["enforce_patch_scope"]

ORIGINAL = (
    '"""Original module header."""\n'
    "\n"
    "def inventory_module(module_name: str) -> dict:\n"
    "    return {'module': module_name}\n"
    "\n"
    "def render_review(module_name: str) -> str:\n"
    "    return module_name\n"
)

TASK = (
    "Add a docstring to inventory_module. "
    "Modify only that function. "
    "Preserve all executable statements."
)


def test_correct_function_docstring_accepted():
    candidate = ORIGINAL.replace(
        "def inventory_module(module_name: str) -> dict:\n",
        "def inventory_module(module_name: str) -> dict:\n"
        '    """Return a small inventory."""\n',
    )
    assert enforce(
        ORIGINAL, candidate, TASK
    ) == "TARGET_FUNCTION_DOCSTRING_ONLY"


def test_wrong_module_docstring_rejected():
    candidate = ORIGINAL.replace(
        "Original module header.",
        "Updated module header.",
    )
    with pytest.raises(ValueError, match="SCOPE_REJECTED"):
        enforce(ORIGINAL, candidate, TASK)


def test_wrong_function_docstring_rejected():
    candidate = ORIGINAL.replace(
        "def render_review(module_name: str) -> str:\n",
        "def render_review(module_name: str) -> str:\n"
        '    """Wrong function."""\n',
    )
    with pytest.raises(ValueError, match="SCOPE_REJECTED"):
        enforce(ORIGINAL, candidate, TASK)


def test_docstring_plus_executable_change_rejected():
    candidate = ORIGINAL.replace(
        "def inventory_module(module_name: str) -> dict:\n",
        "def inventory_module(module_name: str) -> dict:\n"
        '    """Inventory module."""\n',
    ).replace(
        "return {'module': module_name}",
        "return {'module': module_name, 'changed': True}",
    )
    with pytest.raises(ValueError, match="executable"):
        enforce(ORIGINAL, candidate, TASK)


def test_function_signature_change_rejected():
    candidate = ORIGINAL.replace(
        "module_name: str) -> dict:",
        "module_name: int) -> dict:",
    ).replace(
        "def inventory_module(module_name: int) -> dict:\n",
        "def inventory_module(module_name: int) -> dict:\n"
        '    """Inventory module."""\n',
    )
    with pytest.raises(ValueError, match="executable"):
        enforce(ORIGINAL, candidate, TASK)


def test_targeted_function_edit_accepted():
    candidate = ORIGINAL.replace(
        "return {'module': module_name}",
        "return {'module': module_name.strip()}",
    )
    task = "Modify only inventory_module to normalize names."
    assert enforce(
        ORIGINAL, candidate, task
    ) == "TARGET_FUNCTION_ONLY"


def test_targeted_function_plus_unrelated_edit_rejected():
    candidate = ORIGINAL.replace(
        "return {'module': module_name}",
        "return {'module': module_name.strip()}",
    ).replace(
        "return module_name\n",
        "return module_name.upper()\n",
    )
    with pytest.raises(ValueError, match="SCOPE_REJECTED"):
        enforce(
            ORIGINAL,
            candidate,
            "Modify only inventory_module to normalize names.",
        )


def test_ambiguous_function_request_rejected():
    with pytest.raises(ValueError, match="multiple"):
        enforce(
            ORIGINAL,
            ORIGINAL,
            "Modify only inventory_module and render_review.",
        )


def test_unscoped_task_reports_limited_enforcement():
    assert enforce(
        ORIGINAL,
        ORIGINAL,
        "Improve general performance.",
    ) == "NO_EXPLICIT_FUNCTION_SCOPE"


def test_guard_integrated_in_generator_and_applier():
    preview = (
        ROOT / "scripts/neuro_developer_patch_preview.py"
    ).read_text(encoding="utf-8")

    applier = (
        ROOT / "scripts/neuro_developer_patch_apply.py"
    ).read_text(encoding="utf-8")

    ast.parse(preview)
    ast.parse(applier)

    assert "NEUROVEST_CHANGE_SCOPE_GUARD_V1" in preview
    assert "NEUROVEST_CHANGE_SCOPE_GUARD_V1" in applier
    assert "enforce_patch_scope" in preview
    assert "enforce_patch_scope" in applier


def test_existing_self_review_source_remains_parseable():
    source = (
        ROOT
        / "backend/app/stacks/chat_public/developer_self_review.py"
    ).read_text(encoding="utf-8")

    ast.parse(source)
