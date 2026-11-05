
"""Developer-only persisted improvement history tests."""

import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from backend.app.stacks.chat_public.developer_chat_commands import (
    parse_developer_command,
    handle_developer_command,
)
from backend.app.stacks.chat_public.developer_role_guard import (
    authenticated_developer_role,
)

ROOT = Path.home() / "Neurovest"
BASE = ROOT / "backend/app/stacks/chat_public"


def test_natural_language_history_commands():
    phrases = (
        "Hey Neuro, what have you learned about yourself?",
        "Neuro, which problems keep appearing?",
        "Neuro, what should you improve first and why?",
    )
    for phrase in phrases:
        assert parse_developer_command(phrase) == (
            "improvement_history",
        )


def test_normal_user_questions_stay_normal():
    assert parse_developer_command(
        "What did I learn about investing?"
    ) is None


def test_non_developer_is_not_authorized():
    assert not authenticated_developer_role(None)

    for role in (
        "user", "admin", "developer_flagged", "moderator"
    ):
        principal = SimpleNamespace(
            subject="ordinary-user",
            claims={"authorization_role": role},
        )
        assert not authenticated_developer_role(principal)


def test_developer_role_requires_authenticated_claims():
    principal = SimpleNamespace(
        subject="developer-test",
        claims={"authorization_role": "developer"},
    )
    assert authenticated_developer_role(principal)


def test_handler_calls_bounded_internal_reader():
    output = "## Neuro Developer — Improvement Memory"

    with patch("subprocess.run") as mocked:
        mocked.return_value = SimpleNamespace(
            returncode=0,
            stdout=output,
        )
        result = handle_developer_command(
            ("improvement_history",)
        )

    assert result == output
    assert mocked.call_count == 1
    assert mocked.call_args.kwargs["timeout"] == 15


def test_malformed_history_action_is_rejected_without_io():
    with patch("subprocess.run") as mocked:
        result = handle_developer_command(
            ("improvement_history", "unexpected")
        )
    assert "Invalid" in result
    mocked.assert_not_called()


def test_runtime_uses_authenticated_gate():
    source = (BASE / "chat_runtime.py").read_text("utf-8")
    tree = ast.parse(source)
    assert ast.parse(source) is not None
    assert "authenticated_developer_role(principal)" in source
    assert "handle_developer_command(dev_command)" in source

    gate = source.index(
        "and not authenticated_developer_role(principal)"
    )
    dispatch = source.index(
        "handle_developer_command(dev_command)"
    )
    assert gate < dispatch


def test_read_only_sql_and_no_public_route():
    source = (
        ROOT / "scripts/neuro_improvement_history.py"
    ).read_text("utf-8")
    ast.parse(source)
    assert "SET TRANSACTION READ ONLY" in source
    assert "@router." not in source
    assert "apply_unified_diff" not in source


def test_hypothesis_is_explicitly_unverified():
    import runpy
    module = runpy.run_path(
        str(ROOT / "scripts/neuro_improvement_history.py"),
        run_name="history_test",
    )
    prediction, verification, risk = (
        module["hypothesis_for"]("branch_complexity")
    )
    assert prediction and verification and risk

    report = module["summarize"](
        [{
            "scan_id": 1,
            "status": "complete",
            "modules_scanned": 4,
            "modules_allowed": 4,
            "findings_total": 1,
            "findings_new": 1,
            "findings_existing": 0,
        }],
        [{
            "module_name": "developer_chat_commands",
            "function_name": "handle_developer_command",
            "finding_kind": "branch_complexity",
            "priority": "P3",
            "evidence": "Complexity is 40",
            "recommendation": "Simplify branches",
            "seen_count": 1,
            "last_scan_id": 1,
        }],
    )

    assert "has not been executed" in report
    assert "No code changed" in report
