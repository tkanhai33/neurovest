
from pathlib import Path
from types import SimpleNamespace
import asyncio

from backend.app.stacks.chat_public import (
    developer_model_synthesis_v5 as synthesis,
)
from backend.app.stacks.chat_public.developer_grounded_answers_v5 import (
    load_verified_index,
)

ROOT = Path.home() / "Neurovest"
INDEX = ROOT / (
    "runtime/qualification/neuro_v5_developer_candidate/"
    "evidence_index.json"
)

DEVELOPER = SimpleNamespace(
    subject="test-developer",
    claims={"authorization_role": "developer"},
)
THREAD = SimpleNamespace(
    thread_id="test-thread",
    user_id="test-developer",
)


def test_improvement_brief_is_substantive():
    text = synthesis._conversation_quality_brief(
        "Neuro, what do you need to improve first?"
    )
    assert "IMPROVEMENT ASSESSMENT:" in text
    assert "validation or acceptance test" in text
    assert "Do not claim a capability is absent" in text


def test_architecture_brief_distinguishes_observation():
    text = synthesis._conversation_quality_brief(
        "Explain architecture and routing"
    )
    assert "ARCHITECTURE EXPLANATION:" in text
    assert "unverified relationships" in text
    assert "not as proof of runtime behavior" in text


def test_followup_brief_preserves_uncertainty():
    text = synthesis._conversation_quality_brief(
        "Regarding the earlier developer question: "
        "Explain routing\nFollow-up question: Why does that matter?"
    )
    assert "CONTINUATION:" in text
    assert "not as authority" in text


def test_regular_developer_question_gets_basic_guidance():
    text = synthesis._conversation_quality_brief(
        "What can you tell me about this component?"
    )
    assert "Answer the actual question directly" in text
    assert "Never invent citations" in text


def test_existing_allowlist_not_expanded():
    prompt = (
        "ALLOWED SOURCE REFERENCES:\n"
        "backend/app/stacks/chat_public/chat_runtime.py:3516"
        "\n\nVERIFIED STRUCTURAL OBSERVATIONS:"
        "\nExample"
    )
    augmented = prompt + synthesis._conversation_quality_brief(
        "Explain routing"
    )
    assert synthesis._prompt_locations(augmented) == {
        "backend/app/stacks/chat_public/chat_runtime.py:3516"
    }


def test_live_synthesis_passes_quality_brief_to_model():
    verified = load_verified_index(ROOT, INDEX)
    assert len(verified["sources"]) == 24

    prompts = []

    def model(prompt):
        prompts.append(prompt)
        return "Uncited mock response that should not be trusted."

    response = asyncio.run(
        synthesis.synthesize_developer_answer(
            root=ROOT,
            index_path=INDEX,
            question="Explain developer chat routing architecture",
            principal=DEVELOPER,
            thread=THREAD,
            model=model,
        )
    )

    assert prompts
    assert "ARCHITECTURE EXPLANATION:" in prompts[0]
    assert "ALLOWED SOURCE REFERENCES:" in prompts[0]
    assert response != (
        "Uncited mock response that should not be trusted."
    )
