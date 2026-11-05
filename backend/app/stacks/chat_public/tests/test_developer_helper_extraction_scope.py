
"""Controlled helper-extraction scope regression tests."""

import runpy
from pathlib import Path

import pytest

ROOT = Path.home() / "Neurovest"
CHECK = runpy.run_path(
    str(ROOT / "scripts/neuro_developer_patch_scope.py")
)["enforce_patch_scope"]

TASK = "AUTO_REVIEW_EXTRACT_HELPER:inventory_module:_inventory_value"

BEFORE = """
def inventory_module(value: str) -> dict:
    return {"value": value.strip()}

def render_review(value: str) -> str:
    return value
"""

AFTER = """
def inventory_module(value: str) -> dict:
    return {"value": _inventory_value(value)}

def _inventory_value(value: str) -> str:
    return value.strip()

def render_review(value: str) -> str:
    return value
"""


def test_valid_extraction():
    assert CHECK(BEFORE, AFTER, TASK) == (
        "TARGET_FUNCTION_PLUS_ONE_PRIVATE_HELPER"
    )


def test_unrelated_function_change_rejected():
    candidate = AFTER.replace(
        "return value\n",
        "return value.upper()\n",
    )
    with pytest.raises(ValueError, match="SCOPE_REJECTED"):
        CHECK(BEFORE, candidate, TASK)


def test_extra_helper_rejected():
    candidate = AFTER + "\ndef _extra():\n    return 1\n"
    with pytest.raises(ValueError, match="SCOPE_REJECTED"):
        CHECK(BEFORE, candidate, TASK)


def test_target_interface_change_rejected():
    candidate = AFTER.replace(
        "def inventory_module(value: str)",
        "def inventory_module(value: int)",
    )
    with pytest.raises(ValueError, match="interface"):
        CHECK(BEFORE, candidate, TASK)


def test_helper_must_be_called():
    candidate = AFTER.replace(
        "_inventory_value(value)}",
        "value.lower()}",
    )
    with pytest.raises(ValueError, match="does not call"):
        CHECK(BEFORE, candidate, TASK)


def test_helper_import_forbidden():
    candidate = AFTER.replace(
        "def _inventory_value(value: str) -> str:\n",
        "def _inventory_value(value: str) -> str:\n"
        "    import os\n",
    )
    with pytest.raises(ValueError, match="imports"):
        CHECK(BEFORE, candidate, TASK)


def test_malformed_contract_rejected():
    with pytest.raises(ValueError, match="malformed"):
        CHECK(
            BEFORE,
            AFTER,
            "AUTO_REVIEW_EXTRACT_HELPER:inventory_module:public",
        )


def test_missing_target_rejected():
    with pytest.raises(ValueError, match="target"):
        CHECK(
            BEFORE,
            AFTER,
            "AUTO_REVIEW_EXTRACT_HELPER:missing:_inventory_value",
        )


def test_docstring_scope_still_works():
    original = "def inventory_module(x):\n    return x\n"
    candidate = (
        "def inventory_module(x):\n"
        '    """Document the function."""\n'
        "    return x\n"
    )
    assert CHECK(
        original,
        candidate,
        "Add a docstring only to inventory_module.",
    ) == "TARGET_FUNCTION_DOCSTRING_ONLY"
