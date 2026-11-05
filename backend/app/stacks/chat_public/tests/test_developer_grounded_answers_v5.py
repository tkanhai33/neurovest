from pathlib import Path
import hashlib
import json

import pytest

from backend.app.stacks.chat_public.developer_grounded_answers_v5 import (
    EvidenceUnavailable,
    load_verified_index,
    search_definitions,
    answer_developer_question,
    SCHEMA,
)


def fixture_index(tmp_path):
    source = tmp_path / "chat_runtime.py"
    source.write_text("def run_chat_turn(): pass\n")
    index = tmp_path / "index.json"
    index.write_text(json.dumps({
        "schema": SCHEMA,
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
    return index, source


def test_verified_source(tmp_path):
    index, _ = fixture_index(tmp_path)
    data = load_verified_index(tmp_path, index)
    assert search_definitions(
        data, "How does our chat runtime work?"
    )


def test_stale_source_rejected(tmp_path):
    index, source = fixture_index(tmp_path)
    source.write_text("def changed(): pass\n")
    with pytest.raises(EvidenceUnavailable):
        load_verified_index(tmp_path, index)


def test_unauthorized_access(tmp_path):
    index, _ = fixture_index(tmp_path)
    with pytest.raises(PermissionError):
        answer_developer_question(
            root=tmp_path,
            index_path=index,
            question="Explain our chat runtime",
            authorized=False,
        )


def test_grounded_answer(tmp_path):
    index, _ = fixture_index(tmp_path)
    answer = answer_developer_question(
        root=tmp_path,
        index_path=index,
        question="Explain our chat runtime",
        authorized=True,
    )
    assert "run_chat_turn" in answer
    assert "chat_runtime.py:1" in answer
    assert "not verified" in answer


def test_missing_evidence_rejected(tmp_path):
    with pytest.raises(EvidenceUnavailable):
        load_verified_index(
            tmp_path, tmp_path / "missing.json"
        )


def test_no_false_absence_claim(tmp_path):
    index, _ = fixture_index(tmp_path)
    answer = answer_developer_question(
        root=tmp_path,
        index_path=index,
        question="quantum flux capacitor",
        authorized=True,
    )
    assert "does not prove" in answer
