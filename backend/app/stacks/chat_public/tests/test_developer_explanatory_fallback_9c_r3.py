
from pathlib import Path
import pytest

from backend.app.stacks.chat_public import (
    developer_grounded_answers_v5 as grounded,
)

ROOT = Path.home() / "Neurovest"
INDEX = ROOT / (
    "runtime/qualification/neuro_v5_developer_candidate/"
    "evidence_index.json"
)

def ask(question):
    return grounded.answer_developer_question(
        root=ROOT,
        index_path=INDEX,
        question=question,
        authorized=True,
    )

def test_original_contract_preserved():
    result = ask("Explain developer chat routing")
    assert "Verified developer source references" in result
    assert "not verified" in result
    assert "SHA-256" in result
    assert "run_chat_turn" in result

def test_architecture_has_grounded_interpretation():
    result = ask("Explain developer chat routing architecture")
    assert "What the verified evidence establishes" in result
    assert "Architectural interpretation" in result
    assert "runtime or contract evidence" in result

def test_improvement_has_validation_path():
    result = ask("What do you need to improve first?")
    assert "Evidence-driven improvement investigation" in result
    assert "citation accuracy" in result
    assert "context retention" in result
    assert "not completed work" in result

def test_no_matches_no_added_claims():
    assert grounded._nv_explain_verified_fallback(
        "What should improve?", []
    ) == ""

def test_unauthorized_still_denied():
    with pytest.raises(PermissionError):
        ask_unauthorized()

def ask_unauthorized():
    return grounded.answer_developer_question(
        root=ROOT,
        index_path=INDEX,
        question="Explain developer internals",
        authorized=False,
    )
