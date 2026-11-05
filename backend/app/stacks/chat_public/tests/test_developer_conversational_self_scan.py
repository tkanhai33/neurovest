
"""Developer-only self-scan regression tests."""

import ast
from pathlib import Path
from types import SimpleNamespace

from backend.app.stacks.chat_public.developer_chat_commands import (
    parse_developer_command,
    handle_developer_command,
)
from backend.app.stacks.chat_public.developer_role_guard import (
    authenticated_developer_role,
)

ROOT = Path.home() / "Neurovest"
BASE = ROOT / "backend/app/stacks/chat_public"


def test_natural_language_recognized():
    assert parse_developer_command(
        "Hey Neuro, what would help you improve?"
    ) == ("conversational_self_scan",)

    assert parse_developer_command(
        "Neuro, scan yourself for improvements."
    ) == ("conversational_self_scan",)


def test_regular_conversation_not_hijacked():
    for text in (
        "How can I improve my investments?",
        "Can my strategy improve?",
        "What is a stock?",
    ):
        assert parse_developer_command(text) is None


def test_non_developer_principals_denied():
    assert not authenticated_developer_role(None)

    for role in (
        "user",
        "admin",
        "moderator",
        "developer_flagged",
        "owner",
    ):
        principal = SimpleNamespace(
            subject="regular-user",
            claims={"authorization_role": role},
        )
        assert not authenticated_developer_role(principal)


def test_approved_developer_principal():
    principal = SimpleNamespace(
        subject="developer-user",
        claims={"authorization_role": "developer"},
    )
    assert authenticated_developer_role(principal)


def test_runtime_still_enforces_role_before_dispatch():
    source = (BASE / "chat_runtime.py").read_text("utf-8")
    tree = ast.parse(source)

    assert "authenticated_developer_role(principal)" in source

    functions = [
        node for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "handle_chat_message"
    ]
    assert len(functions) == 1

    fn = functions[0]
    lines = source.splitlines()

    gate = next(
        i for i in range(fn.lineno - 1, fn.end_lineno)
        if "and not authenticated_developer_role(principal)"
        in lines[i]
    )

    dispatch = next(
        i for i in range(fn.lineno - 1, fn.end_lineno)
        if "handle_developer_command(dev_command)" in lines[i]
    )

    assert gate < dispatch


def test_self_scan_returns_read_only_report():
    command = parse_developer_command(
        "Hey Neuro, what would help you improve?"
    )
    output = handle_developer_command(command)

    assert "Self-Improvement Scan" in output
    assert "Modules scanned:" in output
    assert "No code was changed" in output


def test_explicit_approval_still_required():
    assert parse_developer_command(
        "/dev apply proposal_20261012_111559_184060_4053474"
    )[0] == "error"
