
import asyncio
import inspect
from pathlib import Path
from backend.app.stacks.chat_public import chat_runtime
from types import SimpleNamespace

from backend.app.stacks.chat_public import developer_model_synthesis_v5 as s
from backend.app.stacks.chat_public.developer_grounded_answers_v5 import load_verified_index

ROOT = Path.home() / "Neurovest"
INDEX = ROOT / "runtime/qualification/neuro_v5_developer_candidate/evidence_index.json"
REF = f"backend/app/stacks/chat_public/chat_runtime.py:{inspect.getsourcelines(chat_runtime.run_chat_turn)[1]}"
DEV = SimpleNamespace(
    subject="synthetic-developer",
    claims={"authorization_role": "developer"},
)
THREAD = SimpleNamespace(
    thread_id="synthetic-thread",
    user_id="synthetic-developer",
)

def ask(candidate):
    prompts = []
    def fake_model(prompt):
        prompts.append(prompt)
        return candidate
    response = asyncio.run(s.synthesize_developer_answer(
        root=ROOT, index_path=INDEX,
        question="Explain developer chat routing architecture.",
        principal=DEV, thread=THREAD, model=fake_model,
    ))
    assert len(prompts) == 1
    return response

def test_structural_claim_accepted():
    text = f"The async function run_chat_turn is defined at `{REF}`."
    assert ask(text) == text

def test_live_execution_false_claim_rejected():
    text = (
        "NeuroVest automatically executes unrestricted "
        f"live broker trades. Confirmed at `{REF}`."
    )
    assert ask(text) != text

def test_auth_claim_rejected():
    text = f"Authentication is guaranteed secure for everyone. `{REF}`"
    assert ask(text) != text

def test_portfolio_claim_rejected():
    text = f"Every portfolio balance is exactly calculated and reconciled. `{REF}`"
    assert ask(text) != text

def test_strategy_claim_rejected():
    text = f"The strategy is proven profitable and outperforms the market. `{REF}`"
    assert ask(text) != text

def test_production_claim_rejected():
    text = f"The production service always handles requests successfully. `{REF}`"
    assert ask(text) != text

def test_denial_preserved():
    text = f"The definition at `{REF}` does not establish live broker execution."
    assert ask(text) == text

def test_contradiction_rejected():
    text = (
        "Live trading is not proven, but NeuroVest "
        f"automatically executes unrestricted live broker trades. `{REF}`"
    )
    assert ask(text) != text

def test_fake_citation_rejected():
    assert ask("The method is at `fake_engine.py:99999`.") != (
        "The method is at `fake_engine.py:99999`."
    )

def test_reason_codes():
    ok, reasons = s._nv9g_claim_evidence_check(
        "Authentication is guaranteed secure. "
        "The portfolio returns are proven accurate."
    )
    assert not ok
    assert "auth_outcome_requires_runtime_evidence" in reasons
    assert "financial_outcome_requires_measurement" in reasons

def test_existing_index():
    assert len(load_verified_index(ROOT, INDEX)["sources"]) == 24
