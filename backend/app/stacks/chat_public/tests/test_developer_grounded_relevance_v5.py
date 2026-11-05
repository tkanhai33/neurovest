from pathlib import Path
import hashlib
import json

from backend.app.stacks.chat_public.developer_grounded_answers_v5 import (
    SCHEMA,
    load_verified_index,
    search_definitions,
    answer_developer_question,
)


def make_index(tmp_path):
    source = tmp_path / "chat_runtime.py"
    source.write_text("def example(): pass\\n")

    names = [
        "run_chat_turn",
        "handle_chat_message",
        "_blocked_training_chat_response",
        "assemble_chat_context",
    ]

    records = [
        {
            "name": name,
            "kind": "function",
            "line": index,
            "syntactic_calls": [],
        }
        for index, name in enumerate(names, 1)
    ]

    index_path = tmp_path / "index.json"
    index_path.write_text(json.dumps({
        "schema": SCHEMA,
        "status": "CANDIDATE_ONLY",
        "sources": {
            "chat_runtime.py": {
                "sha256": hashlib.sha256(
                    source.read_bytes()
                ).hexdigest(),
                "definitions": records,
            },
        },
    }))

    return index_path


def test_broad_runtime_prefers_entry_point(tmp_path):
    index = load_verified_index(
        tmp_path, make_index(tmp_path)
    )
    matches = search_definitions(
        index, "How does our chat runtime work?"
    )
    assert matches[0]["name"] == "run_chat_turn"
    assert matches[1]["name"] == "handle_chat_message"


def test_specific_training_prefers_exact_symbol(tmp_path):
    index = load_verified_index(
        tmp_path, make_index(tmp_path)
    )
    matches = search_definitions(
        index, "Inspect blocked training chat response"
    )
    assert matches[0]["name"] == (
        "_blocked_training_chat_response"
    )


def test_specific_context_prefers_context(tmp_path):
    index = load_verified_index(
        tmp_path, make_index(tmp_path)
    )
    matches = search_definitions(
        index, "Explain assemble chat context"
    )
    assert matches[0]["name"] == "assemble_chat_context"


def test_answer_retains_evidence_disclaimer(tmp_path):
    index_path = make_index(tmp_path)
    answer = answer_developer_question(
        root=tmp_path,
        index_path=index_path,
        question="How does our chat runtime work?",
        authorized=True,
    )
    assert "run_chat_turn" in answer
    assert "not verified" in answer


def test_question_without_matching_terms(tmp_path):
    index = load_verified_index(
        tmp_path, make_index(tmp_path)
    )
    assert not search_definitions(
        index, "quantum banana reactor"
    )
