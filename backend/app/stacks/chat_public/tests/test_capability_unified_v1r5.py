
from backend.app.stacks.chat_public.capability_consistency_audit_v1 import (
    audit_capability_claims,
)

FALSE = [
    "Paper trading is currently disabled on NeuroVest.",
    "You can't run simulated trades at this time.",
    "Paper trading and simulation features are disabled.",
    "Paper trading and simulation are disabled.",
    "As for paper trades, they're currently disabled.",
    "As for paper trading, it's currently disabled.",
    "Simulated trades are unavailable.",
    "You cannot run paper trades right now.",
    "Simulations remain locked.",
    "Paper trades are disabled.",
    "The previous response was wrong, but paper trading is disabled.",
    "That earlier claim was false, however simulations remain locked.",
    "I can execute real brokerage orders.",
    "Personal training changes the global strategy profile.",
]

VALID = [
    "NeuroVest can run simulated paper trades.",
    "Real brokerage orders remain disabled.",
    "Live trading remains locked.",
    "Personal training doesn't change the global strategy profile.",
    "Paper trading is enabled, but live execution is disabled.",
    "Paper trading is not disabled.",
    "Simulation results do not guarantee live profits.",
    "Paper trading is available; real orders are unavailable.",
    "Simulations are enabled while broker execution is disabled.",
    "You cannot run real-money trades.",
    "Paper trading is enabled and live trading remains disabled.",
    "The earlier statement that paper trading is disabled was incorrect.",
    "The previous assistant claim that simulated trades are disabled was wrong.",
    "It is false that paper trading is disabled.",
    "The prior response that paper trading is disabled was mistaken.",
    '"Paper trading is disabled" is false.',
    "The user asked whether paper trading is disabled.",
]


def test_unified_false_claims():
    for statement in FALSE:
        result = audit_capability_claims(statement)
        assert result["review_required"], (statement, result)
        assert result["potential_contradictions"], statement


def test_unified_valid_claims():
    for statement in VALID:
        result = audit_capability_claims(statement)
        assert not result["review_required"], (statement, result)


def test_mixed_correction_and_false_claim():
    statement = (
        "The earlier statement that paper trading is disabled "
        "was incorrect, but simulations remain locked."
    )
    result = audit_capability_claims(statement)
    assert "paper_trading_unavailable" in (
        result["potential_contradictions"]
    )


def test_audit_never_enforces():
    for statement in FALSE + VALID:
        result = audit_capability_claims(statement)
        assert result["mode"] == "audit_only"
        assert result["enforcement_enabled"] is False
        assert statement not in str(result)
