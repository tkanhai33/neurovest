
import pytest

from backend.app.stacks.chat_public.capability_consistency_audit_v1 import (
    audit_capability_claims,
)

FALSE_CLAIMS = [
    "As for simulated paper trades — they’re currently disabled in NeuroVest.",
    "As for simulated paper trades, they're currently disabled.",
    "Simulated paper trades — they are currently unavailable.",
    "Paper trading: it's disabled.",
    "Paper trades; they're locked.",
    "Simulated paper trades are disabled.",
    "Paper trading is currently disabled.",
    "Simulations remain locked.",
    "The user asked a question. Simulated paper trades are disabled.",
    "The user asked whether simulations work, but paper trading is disabled.",
    "The earlier claim was incorrect, but simulated paper trades — they're locked.",
    "They wanted to know whether simulations are disabled. Paper trading is disabled.",
    "As for simulated paper trades — they’re currently disabled in NeuroVest.",
]

VALID_CLAIMS = [
    "The user asked whether simulated paper trades are disabled.",
    "The customer wondered if paper trading is disabled.",
    "They wanted to know whether simulations are disabled.",
    'The user asked, "Are simulated paper trades disabled?"',
    "Paper trading is enabled, but live execution is disabled.",
    "Simulated paper trades are enabled.",
    "Real brokerage execution remains disabled.",
    "Paper trading is not disabled.",
    "The earlier statement that paper trading is disabled was incorrect.",
    "It is false that paper trading is disabled.",
    "If paper trading were disabled, we'd need a replacement.",
    "As for paper trades — they're available, but live orders are disabled.",
    "The user inquired if paper trading is currently disabled.",
    "The user asks whether simulated trades are disabled.",
    "The user wondered whether paper trading is unavailable.",
]

@pytest.mark.parametrize("statement", FALSE_CLAIMS)
def test_false_claim(statement):
    result = audit_capability_claims(statement)
    assert "paper_trading_unavailable" in result["potential_contradictions"], (
        statement, result
    )
    assert result["enforcement_enabled"] is False

@pytest.mark.parametrize("statement", VALID_CLAIMS)
def test_valid_claim(statement):
    result = audit_capability_claims(statement)
    assert result["review_required"] is False, (statement, result)

def test_other_audit_categories_remain():
    result = audit_capability_claims(
        "I can execute real brokerage orders."
    )
    assert "live_broker_permission" in result["potential_contradictions"]

def test_mixed_rejection_and_independent_false_claim():
    result = audit_capability_claims(
        "The earlier statement that paper trading is disabled was incorrect, "
        "but simulated paper trades — they're locked."
    )
    assert "paper_trading_unavailable" in result["potential_contradictions"]
