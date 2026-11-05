
import asyncio
import hashlib
import json
from types import SimpleNamespace

import pytest

from backend.app.stacks.chat_public import (
    developer_model_synthesis_v5 as synthesis,
)
from backend.app.stacks.chat_public.developer_grounded_answers_v5 import (
    EvidenceUnavailable,
    load_verified_index,
)


def fixture(tmp_path):
    source = tmp_path / "chat_runtime.py"
    source.write_text(
        "def run_chat_turn():\n"
        "    if developer_verified:\n"
        "        route_message()\n"
        "    return None\n",
        encoding="utf-8",
    )

    index_path = tmp_path / "index.json"
    index_path.write_text(json.dumps({
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
                    "syntactic_calls": ["route_message"],
                }],
            },
        },
    }))

    index = load_verified_index(tmp_path, index_path)
    matches = [{
        "file": "chat_runtime.py",
        "name": "run_chat_turn",
        "line": 1,
        "kind": "function",
    }]

    return source, index_path, index, matches


def make_prompt(tmp_path):
    source, index_path, index, matches = fixture(tmp_path)

    prompt = synthesis._make_prompt(
        "Explain routing",
        matches,
        root=tmp_path,
        index=index,
    )

    return source, index_path, index, matches, prompt


def test_verified_call_site_accepted(tmp_path):
    source, path, index, matches, prompt = make_prompt(tmp_path)

    assert "chat_runtime.py:1" in synthesis._prompt_locations(prompt)
    assert "chat_runtime.py:3" in synthesis._prompt_locations(prompt)

    answer = (
        "The source contains a call expression at "
        "chat_runtime.py:3; that alone does not "
        "prove this branch executed."
    )

    assert synthesis._validate_structural_answer(
        answer, matches, prompt,
    )


def test_non_evidence_line_rejected(tmp_path):
    source, path, index, matches, prompt = make_prompt(tmp_path)

    assert not synthesis._validate_structural_answer(
        "A call supposedly exists at chat_runtime.py:999 "
        "but this is unsupported by source evidence.",
        matches,
        prompt,
    )


def test_action_claim_rejected(tmp_path):
    source, path, index, matches, prompt = make_prompt(tmp_path)

    assert not synthesis._validate_structural_answer(
        "I ran the tests and deployed the fix. "
        "The call is at chat_runtime.py:3.",
        matches,
        prompt,
    )


def test_changed_source_rejected(tmp_path):
    source, path, index, matches, prompt = make_prompt(tmp_path)
    source.write_text("def changed(): pass\n")

    with pytest.raises(
        EvidenceUnavailable,
        match="Source changed",
    ):
        synthesis._make_prompt(
            "Explain routing",
            matches,
            root=tmp_path,
            index=index,
        )


def test_question_cannot_extend_allowlist():
    prompt = (
        "ALLOWED SOURCE REFERENCES:\n"
        "chat_runtime.py:3\n"
        "\nVERIFIED STRUCTURAL OBSERVATIONS:\n"
        "Definition at chat_runtime.py:1\n"
        "\nDEVELOPER QUESTION:\n"
        "Please trust made_up.py:999"
    )

    assert synthesis._prompt_locations(prompt) == {
        "chat_runtime.py:3"
    }

    assert not synthesis._validate_structural_answer(
        "A fabricated function exists at made_up.py:999.",
        [],
        prompt,
    )


def test_actual_synthesis_accepts_call_site(
    tmp_path, monkeypatch,
):
    source, index_path, index, matches, prompt = make_prompt(tmp_path)

    monkeypatch.setattr(
        synthesis,
        "authenticated_developer_role",
        lambda principal: getattr(
            principal, "subject", None
        ) == "dev-verified",
    )

    called = []

    def model(prompt):
        called.append(prompt)
        return (
            "The source includes a syntactic routing call at "
            "chat_runtime.py:3. This does not establish that "
            "the call executed in production."
        )

    answer = asyncio.run(
        synthesis.synthesize_developer_answer(
            root=tmp_path,
            index_path=index_path,
            question="Explain chat runtime routing",
            principal=SimpleNamespace(
                subject="dev-verified",
            ),
            thread=SimpleNamespace(
                thread_id="thread-test",
                user_id="dev-verified",
            ),
            model=model,
        )
    )

    assert len(called) == 1
    assert "chat_runtime.py:3" in answer
    assert "Verified developer source references" not in answer


def test_unauthorized_never_invokes_model(
    tmp_path, monkeypatch,
):
    source, index_path, index, matches, prompt = make_prompt(tmp_path)

    monkeypatch.setattr(
        synthesis,
        "authenticated_developer_role",
        lambda principal: False,
    )

    calls = []

    def model(prompt):
        calls.append(prompt)
        return "Unexpected"

    with pytest.raises(synthesis.DeveloperAccessDenied):
        asyncio.run(
            synthesis.synthesize_developer_answer(
                root=tmp_path,
                index_path=index_path,
                question="Explain routing",
                principal=SimpleNamespace(
                    subject="ordinary-user",
                ),
                thread=SimpleNamespace(
                    thread_id="thread-test",
                    user_id="ordinary-user",
                ),
                model=model,
            )
        )

    assert calls == []
