
import ast
import hashlib
import json

from backend.app.stacks.chat_public.developer_model_synthesis_v5 import (
    _make_prompt,
)
from backend.app.stacks.chat_public.developer_grounded_answers_v5 import (
    load_verified_index,
)


def test_structural_evidence_uses_verified_source(tmp_path):
    source = tmp_path / "chat_runtime.py"
    source.write_text(
        "def run_chat_turn():\n"
        "    if verified_developer:\n"
        "        route_message()\n"
        "    return None\n",
        encoding="utf-8",
    )

    path = tmp_path / "index.json"
    path.write_text(json.dumps({
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
                    "syntactic_calls": [
                        "route_message",
                    ],
                }],
            }
        },
    }))

    index = load_verified_index(tmp_path, path)

    prompt = _make_prompt(
        "How does routing work?",
        [{
            "file": "chat_runtime.py",
            "name": "run_chat_turn",
            "line": 1,
            "kind": "function",
        }],
        root=tmp_path,
        index=index,
    )

    assert "CALL: route_message" in prompt
    assert "CONDITION_VARIABLES: verified_developer" in prompt
    assert "chat_runtime.py:3" in prompt
    assert "runtime execution" in prompt


def test_unindexed_source_is_not_read(tmp_path):
    source = tmp_path / "secret.py"
    source.write_text(
        "def sensitive():\n"
        "    leak_sensitive_information()\n"
    )

    prompt = _make_prompt(
        "Explain this",
        [{
            "file": "secret.py",
            "name": "sensitive",
            "line": 1,
            "kind": "function",
        }],
        root=tmp_path,
        index={"sources": {}},
    )

    assert "leak_sensitive_information" not in prompt


def test_prompt_uses_full_relative_paths():
    prompt = _make_prompt(
        "Explain developer roles",
        [{
            "file": (
                "backend/app/stacks/chat_public/"
                "developer_role_guard.py"
            ),
            "name": "authenticated_developer_role",
            "line": 8,
            "kind": "function",
        }],
    )

    assert (
        "backend/app/stacks/chat_public/"
        "developer_role_guard.py:8"
    ) in prompt
    assert "Do not shorten file paths" in prompt
