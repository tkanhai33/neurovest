
from backend.app.stacks.chat_public.financial_grounding_g43_r56 import (
    guidance, problematic_claims, review, topics,
)

def test_tfsa_reference():
    text = guidance("Explain TFSA withdrawal room.")
    assert "NEXT calendar year" in text
    assert "canada.ca" in text

def test_rrsp_reference():
    text = guidance("Explain RRSP unused contribution room.")
    assert "no general 15-year expiry" in text

def test_fhsa_reference():
    text = guidance("How do FHSA withdrawals work?")
    assert "non-qualifying withdrawal" in text.lower()

def test_general_chat_not_changed():
    assert guidance("Tell me about gravitational waves") == ""
    assert topics("Hello") == ()

def test_known_financial_issue():
    result = problematic_claims(
        "Explain TFSA rules",
        "Withdrawn funds immediately become available "
        "for recontribution in the same calendar year.",
    )
    assert "tfsa_same_year_recontribution_claim" in result

def test_developer_answer_preserved():
    original = "Verified developer evidence reply"
    result, flags = review(
        "TFSA developer audit",
        original,
        protected_developer=True,
    )
    assert result == original
    assert flags == ()
