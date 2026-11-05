from pathlib import Path

import pytest

from backend.app.stacks.chat_public.developer_self_review import (
    inventory_module,
    render_review,
)
from backend.app.stacks.chat_public.developer_chat_commands import (
    parse_developer_command,
    handle_developer_command,
)


def test_review_command_parses():
    assert parse_developer_command(
        "/dev review developer_repository_inspection"
    ) == ("review", "developer_repository_inspection")


def test_review_requires_exact_arguments():
    assert parse_developer_command("/dev review")[0] == "error"
    assert parse_developer_command(
        "/dev review developer_repository_inspection extra"
    )[0] == "error"


def test_review_rejects_unapproved_module():
    result = render_review("main")
    assert "outside the self-review scope" in result


def test_inventory_reports_functions():
    report = inventory_module("developer_repository_inspection")
    assert report["function_count"] > 0
    assert report["file"].endswith(
        "developer_repository_inspection.py"
    )


def test_review_contains_actual_source_reference():
    result = render_review("developer_repository_inspection")
    assert "Source SHA256" in result
    assert "Functions inventoried" in result


def test_review_handler_uses_existing_chat_command():
    result = handle_developer_command(
        ("review", "developer_repository_inspection")
    )
    assert "Function Self-Review" in result


def test_review_does_not_modify_source():
    path = (
        Path.home() / "Neurovest"
        / "backend/app/stacks/chat_public/"
        / "developer_repository_inspection.py"
    )
    before = path.read_bytes()
    inventory_module("developer_repository_inspection")
    assert path.read_bytes() == before
