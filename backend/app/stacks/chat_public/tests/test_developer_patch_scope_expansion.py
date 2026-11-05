
"""Verify Neuro's expanded developer patch scope."""

import ast
import runpy
from pathlib import Path

ROOT = Path.home() / "Neurovest"

OLD = (
    "backend/app/stacks/chat_public/"
    "developer_repository_inspection.py"
)

NEW = (
    "backend/app/stacks/chat_public/"
    "developer_self_review.py"
)

CHAT = (
    "backend/app/stacks/chat_public/"
    "developer_chat_commands.py"
)


def test_applier_has_exactly_two_approved_modules():
    namespace = runpy.run_path(
        str(ROOT / "scripts/neuro_developer_patch_apply.py")
    )

    allowed = namespace["ALLOWED"]

    assert set(allowed) == {OLD, NEW}
    assert len(allowed[OLD]) >= 3
    assert len(allowed[NEW]) >= 2

    for relative, tests in allowed.items():
        assert all(
            (ROOT / test).is_file()
            for test in tests
        )


def test_chat_accepts_both_approved_modules():
    namespace = runpy.run_path(str(ROOT / CHAT))
    parse = namespace["parse_developer_command"]

    for source in (OLD, NEW):
        command = parse(
            "/dev propose "
            + source
            + " :: Extract a focused helper with regression tests"
        )

        assert command[0] == "propose"
        assert command[1] == source


def test_chat_rejects_unapproved_sources():
    namespace = runpy.run_path(str(ROOT / CHAT))
    parse = namespace["parse_developer_command"]

    for source in (
        "backend/app/main.py",
        "backend/app/stacks/identity_auth/login_service.py",
        "backend/app/stacks/broker_integration/broker_api.py",
    ):
        command = parse(
            "/dev propose "
            + source
            + " :: Modify this source file with a patch"
        )

        assert command[0] == "error"


def test_approval_still_requires_explicit_flag():
    namespace = runpy.run_path(str(ROOT / CHAT))
    parse = namespace["parse_developer_command"]

    proposal_id = "proposal_20261012_103746_896834_4048392"

    assert parse(
        "/dev apply " + proposal_id
    )[0] == "error"

    assert parse(
        "/dev apply " + proposal_id + " --approve"
    ) == ("apply", proposal_id)


def test_api_still_uses_authenticated_developer_guard():
    source = (
        ROOT
        / "backend/app/stacks/chat_public/developer_code_api.py"
    ).read_text(encoding="utf-8")

    tree = ast.parse(source)

    require = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "_require_developer"
    ]

    assert len(require) == 1

    assert "authenticated_developer_role" in (
        ast.get_source_segment(source, require[0]) or ""
    )


def test_self_review_module_exists_and_parses():
    path = ROOT / NEW
    assert path.is_file()
    ast.parse(path.read_text(encoding="utf-8"))
