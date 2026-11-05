import asyncio
from types import SimpleNamespace

from backend.app.stacks.chat_public import (
    developer_awareness_integration_v5 as integration,
)


def identity(owner="developer", thread_owner="developer"):
    return (
        SimpleNamespace(subject=owner),
        SimpleNamespace(
            thread_id="test-thread",
            user_id=thread_owner,
        ),
    )


def invoke(tmp_path, principal, thread):
    return asyncio.run(
        integration.maybe_grounded_developer_answer(
            root=tmp_path,
            principal=principal,
            thread=thread,
            question="Explain our chat routing",
        )
    )


def test_disabled_flag_skips_auth_and_model(
    monkeypatch, tmp_path,
):
    monkeypatch.delenv(
        "NEURO_V5_GROUNDED_AWARENESS",
        raising=False,
    )

    def unexpected(_):
        raise AssertionError(
            "Authorization should not be evaluated"
        )

    monkeypatch.setattr(
        integration,
        "authenticated_developer_role",
        unexpected,
    )

    principal, thread = identity()
    assert invoke(tmp_path, principal, thread) is None


def test_normal_user_denied(monkeypatch, tmp_path):
    monkeypatch.setenv(
        "NEURO_V5_GROUNDED_AWARENESS", "1"
    )
    monkeypatch.setattr(
        integration,
        "authenticated_developer_role",
        lambda principal: False,
    )

    principal, thread = identity()
    assert invoke(tmp_path, principal, thread) is None


def test_cross_owner_thread_denied(
    monkeypatch, tmp_path,
):
    monkeypatch.setenv(
        "NEURO_V5_GROUNDED_AWARENESS", "1"
    )
    monkeypatch.setattr(
        integration,
        "authenticated_developer_role",
        lambda principal: True,
    )

    principal, thread = identity(
        thread_owner="another-user"
    )

    assert invoke(tmp_path, principal, thread) is None


def test_invalid_question_denied(
    monkeypatch, tmp_path,
):
    monkeypatch.setenv(
        "NEURO_V5_GROUNDED_AWARENESS", "1"
    )
    monkeypatch.setattr(
        integration,
        "authenticated_developer_role",
        lambda principal: True,
    )

    principal, thread = identity()

    result = asyncio.run(
        integration.maybe_grounded_developer_answer(
            root=tmp_path,
            principal=principal,
            thread=thread,
            question="",
        )
    )

    assert result is None


def test_runtime_self_review_precedence():
    from pathlib import Path
    import ast

    path = (
        Path(__file__).resolve().parents[1]
        / "chat_runtime.py"
    )

    source = path.read_text("utf-8")
    tree = ast.parse(source)

    assert source.count(
        "NV_V5_GROUNDED_INTEGRATION"
    ) == 1

    review = source.index(
        "if _self_review_exact:"
    )
    guarded_else = source.index(
        "NV_V5_GROUNDED_INTEGRATION"
    )
    legacy = source.index(
        "_v3_result = await _v3_explain("
    )

    assert review < guarded_else < legacy
    assert "if _nv5_answer is not None:" in source
