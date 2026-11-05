
import asyncio
import inspect
from pathlib import Path
from backend.app.stacks.chat_public import chat_runtime
from types import SimpleNamespace

from backend.app.stacks.chat_public import (
    developer_model_synthesis_v5 as synthesis,
)

ROOT = Path.home() / "Neurovest"
INDEX = ROOT / (
    "runtime/qualification/neuro_v5_developer_candidate/"
    "evidence_index.json"
)
CITATION = (
    "backend/app/stacks/chat_public/chat_runtime.py:"
    f"{inspect.getsourcelines(chat_runtime.run_chat_turn)[1]}"
)

DEV = SimpleNamespace(
    subject="synthetic-developer",
    claims={"authorization_role": "developer"},
)
THREAD = SimpleNamespace(
    thread_id="synthetic-thread",
    user_id="synthetic-developer",
)

def ask(candidate):
    calls = []
    def model(prompt):
        calls.append(prompt)
        return candidate

    result = asyncio.run(
        synthesis.synthesize_developer_answer(
            root=ROOT,
            index_path=INDEX,
            question="Explain developer chat routing architecture.",
            principal=DEV,
            thread=THREAD,
            model=model,
        )
    )
    assert len(calls) == 1
    return result

def test_observed_false_claim_rejected():
    candidate = (
        "NeuroVest automatically executes unrestricted "
        "live broker trades whenever a user asks it to. "
        f"This behavior is confirmed at `{CITATION}`."
    )
    result = ask(candidate)
    assert result != candidate
    assert result.startswith(
        "## Verified developer source references"
    )

def test_real_money_order_claim_rejected():
    candidate = (
        "The system sends real-money broker orders "
        f"automatically. See `{CITATION}`."
    )
    assert ask(candidate) != candidate

def test_direct_guard():
    assert synthesis._nv9f_unsupported_execution_claim(
        "We automatically place live broker trades."
    )

def test_negation_preserved():
    assert not synthesis._nv9f_unsupported_execution_claim(
        "We do not automatically place live broker trades."
    )

def test_contrast_rejected():
    assert synthesis._nv9f_unsupported_execution_claim(
        "We do not send paper orders, but we "
        "automatically execute live broker trades."
    )

def test_structural_answer_preserved():
    candidate = (
        "The asynchronous function `run_chat_turn` is "
        f"defined at `{CITATION}`. Its definition does "
        "not prove live broker orders are executed."
    )
    assert ask(candidate) == candidate

def test_fake_citation_rejected():
    candidate = (
        "The function exists at "
        "`nonexistent_executor.py:99999`."
    )
    assert ask(candidate) != candidate

def test_negative_then_positive_sentences_rejected():
    assert synthesis._nv9f_unsupported_execution_claim(
        "Live broker trading is not enabled. "
        "We automatically send live broker orders."
    )

def test_no_model_execution_claim_is_accepted_without_citation():
    assert ask(
        "We automatically execute live broker orders."
    ) != "We automatically execute live broker orders."
