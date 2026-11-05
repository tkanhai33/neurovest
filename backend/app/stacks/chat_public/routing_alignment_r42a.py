"""R42A: conservative, read-only classification alignment.

This module only refines educational classification and model depth.
It cannot create privileges or trigger retrieval or trading.
"""
from __future__ import annotations

import re
from dataclasses import replace

TECHNICAL = re.compile(
    r"\b(?:CAP theorem|consistency and availability|"
    r"network partition|distributed systems?|"
    r"weak convergence|strong convergence|"
    r"sigma[- ]algebra|conditional expectation|"
    r"measurement problem|quantum mechanics|"
    r"data contamination|benchmark leakage|"
    r"functional analysis|Hilbert spaces?)\b",
    re.I,
)

FINANCE_ACCOUNTS = re.compile(
    r"\b(?:TFSA|RRSP|RRIF|FHSA|RESP)\b",
    re.I,
)

FINANCE_EDUCATION = re.compile(
    r"\b(?:what is|what are|explain|compare|"
    r"difference|distinguish|define|describe|"
    r"how does|how do|tax treatment|"
    r"contribution treatment)\b",
    re.I,
)

RESTRICTED = re.compile(
    r"\b(?:place|execute|submit|send|enable|"
    r"buy|sell|trade|broker|live order|"
    r"emergency stop|emergency_stop|"
    r"admin|developer|repository|"
    r"my account|my holdings|my portfolio)\b",
    re.I,
)

REASONING = re.compile(
    r"\b(?:prove|derive|demonstrate rigorously|"
    r"measurement problem|weak convergence|"
    r"strong convergence|conditional expectation|"
    r"sigma[- ]algebra|CAP theorem|"
    r"data contamination|benchmark leakage|"
    r"functional analysis|Hilbert spaces?)\b",
    re.I,
)

def align_intent(message, decision):
    if not isinstance(message, str) or len(message) > 12000:
        return decision

    if getattr(decision, "blocked", False):
        return decision

    if getattr(decision, "developer_mode", False):
        return decision

    if getattr(decision, "architecture_mode", False):
        return decision

    if getattr(decision, "self_evaluation", False):
        return decision

    if getattr(decision, "intent", "") not in (
        "general_conversation",
        "trading_conversation",
    ):
        return decision

    if RESTRICTED.search(message):
        return decision

    if TECHNICAL.search(message):
        return replace(
            decision,
            intent="general_conversation",
            symbol=None,
            family="GENERAL",
            subtype="technical_education",
            confidence=0.95,
        )

    if FINANCE_ACCOUNTS.search(message) and FINANCE_EDUCATION.search(message):
        return replace(
            decision,
            intent="trading_conversation",
            symbol=None,
            family="MARKET",
            subtype="general_finance_reasoning",
            confidence=0.95,
        )

    return decision


def align_cognitive(message, decision):
    if not isinstance(message, str) or len(message) > 12000:
        return decision

    if RESTRICTED.search(message):
        return decision

    if getattr(decision, "tier", None) != "fast":
        return decision

    if getattr(decision, "family", None) != "GENERAL":
        return decision

    if getattr(decision, "subtype", None) != "technical_education":
        return decision

    if not REASONING.search(message):
        return decision

    return replace(
        decision,
        tier="reason",
        model="neuro-reason:latest",
        reason="R42A: advanced nonfinancial technical reasoning",
    )
