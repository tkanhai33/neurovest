"""Capability consistency audit-only regression coverage."""

from pathlib import Path

import pytest

from backend.app.stacks.chat_public.capability_consistency_audit_v1 import (
    audit_capability_claims,
)


@pytest.mark.parametrize(
    "statement,expected",
    [
        ("I can place real brokerage orders.", True),
        ("I cannot place real brokerage orders.", False),
        ("Paper trading is disabled.", True),
        ("Simulated trading remains locked.", True),
        ("Paper trading is enabled.", False),
        ("Simulations are not disabled.", False),
        ("Can NeuroVest execute real orders?", False),
        ("Someone asked whether NeuroVest can execute live trades.", False),
        ("I automatically retrain my language model from user conversations.", True),
        ("I do not automatically retrain my language model from conversations.", False),
        ("Personal strategy training directly modifies the global strategy profile.", True),
        ("Personal strategy training cannot modify the global strategy profile.", False),
        (
            "Someone asked whether NeuroVest can execute live trades. "
            "Paper trading is disabled.",
            True,
        ),
        (
            "Paper trading is enabled. "
            "NeuroVest can execute real orders.",
            True,
        ),
    ],
)
def test_capability_audit_examples(statement, expected):
    result = audit_capability_claims(statement)
    assert result["review_required"] is expected
    assert result["enforcement_enabled"] is False


def test_audit_does_not_return_sensitive_answer_text():
    result = audit_capability_claims(
        "My private account identifier is 123456789. "
        "Paper trading is disabled."
    )
    assert "123456789" not in str(result)


def test_verifier_integration_is_audit_only():
    verifier = (
        Path(__file__).resolve().parents[1]
        / "response_verification.py"
    ).read_text(encoding="utf-8")

    assert "NEUROVEST_CAPABILITY_CONSISTENCY_AUDIT_V1" in verifier
    assert '"capability_consistency_audit":' in verifier
    assert "audit_capability_claims(final_response)" in verifier
