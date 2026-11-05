import asyncio
import hashlib
import json
from types import SimpleNamespace

import pytest

from backend.app.stacks.chat_public import (
    developer_model_synthesis_v5 as s,
)


def make_index(tmp_path):
    source = tmp_path / "chat_runtime.py"
    source.write_text("def run_chat_turn(): pass\n")

    index = tmp_path / "evidence.json"
    index.write_text(json.dumps({
        "schema": "neurovest_v5_ast_evidence_candidate_v1",
        "status": "CANDIDATE_ONLY",
        "sources": {
            "chat_runtime.py": {
                "sha256": hashlib.sha256(
                    source.read_bytes()
                ).hexdigest(),
                "definitions": [{
                    "name": "run_chat_turn",
                    "kind": "function",
                    "line": 1,
                    "syntactic_calls": [],
                }],
            },
        },
    }))
    return index


def identities(owner="dev-1", thread_owner="dev-1"):
    return (
        SimpleNamespace(subject=owner),
        SimpleNamespace(
            thread_id="thread-1",
            user_id=thread_owner,
        ),
    )


@pytest.fixture(autouse=True)
def mock_authorization(monkeypatch):
    monkeypatch.setattr(
        s,
        "authenticated_developer_role",
        lambda principal: (
            getattr(principal, "subject", "") == "dev-1"
        ),
    )


def run(tmp_path, model, *, principal=None, thread=None):
    default_principal, default_thread = identities()

    return asyncio.run(s.synthesize_developer_answer(
        root=tmp_path,
        index_path=make_index(tmp_path),
        question="Explain chat runtime",
        principal=principal or default_principal,
        thread=thread or default_thread,
        model=model,
    ))


def test_async_model_response(tmp_path):
    observed = []

    async def model(prompt):
        observed.append(prompt)
        return (
            "The definition at chat_runtime.py:1 exists. "
            "This alone does not prove runtime execution."
        )

    result = run(tmp_path, model)
    assert "runtime execution" in result
    assert len(observed) == 1


def test_sync_model_response(tmp_path):
    result = run(
        tmp_path,
        lambda prompt: (
            "The source contains chat_runtime.py:1, "
            "but execution behaviour is not established."
        ),
    )
    assert "execution behaviour" in result


def test_fake_citation_falls_back(tmp_path):
    result = run(
        tmp_path,
        lambda prompt: (
            "The invented component at made_up.py:999 "
            "definitely places broker orders."
        ),
    )
    assert "Verified developer source references" in result
    assert "made_up.py" not in result


def test_model_exception_falls_back(tmp_path):
    def model(prompt):
        raise RuntimeError("Model unavailable")

    result = run(tmp_path, model)
    assert "Verified developer source references" in result


def test_unauthorized_never_calls_model(tmp_path):
    calls = []
    principal, thread = identities(owner="ordinary-user")

    def model(prompt):
        calls.append(prompt)
        return "Should never run"

    with pytest.raises(s.DeveloperAccessDenied):
        run(
            tmp_path, model,
            principal=principal,
            thread=thread,
        )
    assert calls == []


def test_wrong_thread_owner_denied(tmp_path):
    principal, thread = identities(
        thread_owner="another-user"
    )
    with pytest.raises(s.DeveloperAccessDenied):
        run(
            tmp_path, None,
            principal=principal,
            thread=thread,
        )


def test_false_test_success_falls_back(tmp_path):
    result = run(
        tmp_path,
        lambda prompt: (
            "I ran the tests and everything passed. "
            "The symbol is at chat_runtime.py:1."
        ),
    )
    assert "I ran the tests" not in result
    assert "Verified developer source references" in result


def test_stale_source_rejected(tmp_path):
    index = make_index(tmp_path)
    (tmp_path / "chat_runtime.py").write_text(
        "def replaced(): pass\n"
    )
    principal, thread = identities()

    with pytest.raises(Exception, match="Indexed source changed"):
        asyncio.run(s.synthesize_developer_answer(
            root=tmp_path,
            index_path=index,
            question="Explain chat runtime",
            principal=principal,
            thread=thread,
            model=None,
        ))


def test_no_model_uses_evidence_fallback(tmp_path):
    result = run(tmp_path, None)
    assert "Verified developer source references" in result
