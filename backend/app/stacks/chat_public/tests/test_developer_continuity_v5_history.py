from pathlib import Path
from types import SimpleNamespace

from backend.app.stacks.chat_public.developer_continuity_v5 import (
    select_previous_user,
    continuation_question,
)

BASE = Path(__file__).resolve().parents[1]


def row(mid, role, content):
    return SimpleNamespace(
        message_id=mid,
        role=role,
        content=content,
    )


def test_newest_first_previous_user():
    rows = [
        row("3", "user", "Which functions are responsible?"),
        row("2", "assistant", "Routing overview"),
        row("1", "user", "Inspect our chat routing."),
    ]
    assert select_previous_user(
        rows, current_message_id="3"
    ) == "Inspect our chat routing."


def test_no_current_message_fails_closed():
    rows = [
        row("2", "assistant", "Old response"),
        row("1", "user", "Inspect our chat routing."),
    ]
    assert select_previous_user(
        rows, current_message_id="3"
    ) == ""


def test_older_subject_not_inherited():
    rows = [
        row("5", "user", "Which functions are responsible?"),
        row("4", "assistant", "Weather forecast"),
        row("3", "user", "What is the weather?"),
        row("2", "assistant", "Architecture summary"),
        row("1", "user", "Inspect our chat routing."),
    ]
    prior = select_previous_user(
        rows, current_message_id="5"
    )
    assert prior == "What is the weather?"
    assert continuation_question(
        message="Which functions are responsible?",
        previous_user=prior,
        verified_developer=True,
    ) is None


def test_runtime_requests_newest_first():
    source = (BASE / "chat_runtime.py").read_text(
        encoding="utf-8"
    )
    assert (
        "limit=8,\n"
        "                    oldest_first=False,"
    ) in source
    assert "_nv5_select_previous_user(" in source


def test_current_message_not_selected_as_previous():
    rows = [
        row("7", "user", "Which functions are responsible?"),
    ]
    assert select_previous_user(
        rows, current_message_id="7"
    ) == ""
