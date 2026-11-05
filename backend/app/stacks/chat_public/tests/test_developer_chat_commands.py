from unittest.mock import patch

from backend.app.stacks.chat_public.developer_chat_commands import (
    ALLOWED_SOURCE,
    handle_developer_command,
    parse_developer_command,
)


def test_parse_explicit_proposal_command():
    command = parse_developer_command(
        "/dev propose "
        + ALLOWED_SOURCE
        + " :: Improve implementation file ranking"
    )

    assert command == (
        "propose",
        ALLOWED_SOURCE,
        "Improve implementation file ranking",
    )


def test_normal_chat_is_not_intercepted():
    assert parse_developer_command(
        "Explain the NeuroVest architecture"
    ) is None


def test_unapproved_path_is_rejected():
    command = parse_developer_command(
        "/dev propose backend/app/main.py "
        ":: Rewrite the whole application"
    )

    assert command[0] == "error"


def test_invalid_proposal_id_rejected():
    command = parse_developer_command(
        "/dev show ../../etc/passwd"
    )

    assert command[0] == "error"


def test_show_missing_proposal():
    result = handle_developer_command(
        ("show", "proposal_20000101_000000_1_1")
    )

    assert "not found" in result.lower()


def test_generator_not_called_for_disallowed_file():
    with patch(
        "backend.app.stacks.chat_public."
        "developer_chat_commands.subprocess.run"
    ) as runner:

        result = handle_developer_command(
            (
                "propose",
                "backend/app/main.py",
                "Modify protected application source",
            )
        )

        assert "not allowed" in result
        runner.assert_not_called()


# NEUROVEST_CHAT_PATCH_APPROVAL_V1

def test_patch_requires_exact_approval_phrase():
    assert parse_developer_command(
        "/dev apply proposal_20261012_090103_581297_4018475"
    )[0] == "error"


def test_patch_requires_valid_proposal_id():
    assert parse_developer_command(
        "/dev apply ../../etc/passwd --approve"
    )[0] == "error"


def test_patch_approval_parses_specific_id():
    proposal_id = "proposal_20261012_090103_581297_4018475"

    assert parse_developer_command(
        f"/dev apply {proposal_id} --approve"
    ) == ("apply", proposal_id)


def test_normal_approval_message_does_not_apply():
    for message in ("yes", "approve", "go ahead", "apply it"):
        assert parse_developer_command(message) is None


def test_apply_rejects_missing_proposal_without_subprocess():
    with patch(
        "backend.app.stacks.chat_public."
        "developer_chat_commands.subprocess.run"
    ) as runner:
        response = handle_developer_command(
            ("apply", "proposal_20000101_000000_1_1")
        )

        assert "not found" in response.lower()
        runner.assert_not_called()


def test_apply_rejects_malformed_internal_command():
    with patch(
        "backend.app.stacks.chat_public."
        "developer_chat_commands.subprocess.run"
    ) as runner:
        response = handle_developer_command(
            ("apply", "../../somewhere")
        )

        assert "invalid" in response.lower()
        runner.assert_not_called()
