"""G43-R41E: conservative inference-depth enhancement.

Model selection only. Never changes permissions, account scope,
retrieval authorization, execution routes, or tool access.
"""
from __future__ import annotations

import re
import dataclasses
from dataclasses import is_dataclass, replace

MARKER = "NEUROVEST_G43_R41E_REASONING_SELECTION"

REASON_MODEL = "neuro-reason:latest"

ADVANCED_PATTERNS = tuple(re.compile(p, re.I) for p in (
    r"\bweak\s+(?:and|vs\.?|versus)\s+strong\s+convergence\b",
    r"\b(?:weak|strong)\s+convergence\b",
    r"\b(?:convergence|functions?)\s+in\s+(?:l2|l\^2|ℓ2|ℓ\^2)\b",
    r"\bsigma[- ]algebra\b",
    r"\bconditional expectation\b",
    r"\bmeasurement problem\b",
    r"\bdata contamination\b.*\bbenchmark\b",
    r"\bbenchmark\b.*\bdata contamination\b",
    r"\bCAP theorem\b",
    r"\bput-call parity\b",
    r"\bEuler[- ]Lagrange\b",
    r"\b(?:prove|derive|demonstrate rigorously)\b"
    r".*\b(?:theorem|equation|identity|operator|convergence)\b",
))

def upgrade_reasoning_decision(message, decision):
    """Return a model-depth upgrade or the original decision.

    Restricted to general educational reasoning; no market, user
    account, trading, or retrieval capability is introduced.
    """
    if not isinstance(message, str):
        return decision
    if not is_dataclass(decision):
        return decision

    if getattr(decision, "tier", None) != "fast":
        return decision

    if getattr(decision, "retrieval_required", False):
        return decision

    # Do not alter specialist market/trading routes or user tools.
    # Only general discussion and the known false-positive
    # stock-lookup classification are eligible for escalation.
    family = getattr(decision, "family", "")
    subtype = getattr(decision, "subtype", "")

    matched = any(p.search(message) for p in ADVANCED_PATTERNS)
    if not matched:
        return decision

    if family not in ("GENERAL", "MARKET"):
        return decision

    if family == "MARKET":
        if subtype != "stock_lookup":
            return decision
        # CAP theorem is clearly not a finance/trading request.
        if not re.search(r"\bCAP theorem\b", message, re.I):
            return decision

    fields = {field.name for field in dataclasses.fields(decision)}
    changes = {}

    for name, value in (
        ("tier", "reason"),
        ("model", REASON_MODEL),
        ("reason", "R41E: advanced technical reasoning requires deeper inference."),
    ):
        if name in fields:
            changes[name] = value

    # Never change family/subtype/intent or tool flags here:
    # those belong to separate, authorization-aware routing.
    try:
        return replace(decision, **changes)
    except (TypeError, ValueError):
        return decision
