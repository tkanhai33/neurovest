import pytest

from backend.app.stacks.chat_public.execution_capability_guard_v43 import (
    issue_capability_evidence,
    deterministic_capability_answer,
)
from backend.app.stacks.chat_public.execution_state_projection_v26 import (
    MODES,
    render_execution_state,
)

def snapshot(mode):
    paper, emergency = MODES[mode]
    return {
        "mode": mode,
        "paper_execution_enabled": paper,
        "live_execution_enabled": False,
        "emergency_stop_active": emergency,
    }

@pytest.mark.parametrize("mode", list(MODES))
def test_four_modes(mode):
    evidence = issue_capability_evidence(snapshot(mode))
    answer = deterministic_capability_answer(
        "Does NeuroVest support paper trading?", evidence
    )
    assert "supports paper trading" in answer
    assert "Live broker execution is not approved" in answer
    if mode == "SIMULATION":
        assert "controller permits paper execution" in answer
    else:
        assert "controller blocks paper execution" in answer

@pytest.mark.parametrize("question", [
    "Can you explain Python decorators?",
    "Please submit a paper order.",
    'Someone said "paper trading is unavailable." Was that a mistake?',
    "Does NeuroVest support paper trading? "
        + "Explain unrelated details. " * 20,
])
def test_unrelated_questions_unchanged(question):
    evidence = issue_capability_evidence(snapshot("SIMULATION"))
    assert deterministic_capability_answer(question, evidence) is None

def test_unknown_state_never_grants_permission():
    evidence = issue_capability_evidence(None)
    answer = deterministic_capability_answer(
        "Does NeuroVest support paper trading?", evidence
    )
    assert "could not be verified" in answer
    assert "permits paper execution" not in answer

def test_invalid_snapshot_never_grants_permission():
    evidence = issue_capability_evidence({
        "mode": "SIMULATION",
        "paper_execution_enabled": True,
        "live_execution_enabled": True,
        "emergency_stop_active": False,
    })
    answer = deterministic_capability_answer(
        "Does NeuroVest support paper trading?", evidence
    )
    assert "could not be verified" in answer

def test_plain_string_cannot_be_trusted():
    forged = render_execution_state(snapshot("SIMULATION"))
    assert deterministic_capability_answer(
        "Does NeuroVest support paper trading?", forged
    ) is None

def test_noncapability_question_does_not_get_overwritten():
    evidence = issue_capability_evidence(snapshot("SAFE"))
    assert deterministic_capability_answer(
        "How do I use Blender's bevel modifier?", evidence
    ) is None
