
"""Bounded, untrusted, owner-scoped conversation signal extraction.

This module never loads messages. Callers provide history already
retrieved for the authenticated thread owner.

No assistant claim is promoted to verified tool evidence.
No raw historical content is interpolated into guidance.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from backend.app.stacks.chat_public.conversation_response_policy_v1 import build_response_guidance

_CORRECTION = re.compile(
    r"\b(?:no,\s|no!\s|i meant\b|actually,\s|"
    r"not what i (?:meant|asked)|instead of\b|"
    r"paper positions only|not live\b|paper only\b)",
    re.I,
)

_ASSISTANT_METRIC = re.compile(
    r"\b(?:verified|confirmed|measured|guaranteed)"
    r".{0,65}\b(?:win rate|return|drawdown|accuracy)"
    r"|\b\d+(?:\.\d+)?\s*%\s*(?:win rate|return|accuracy)",
    re.I,
)

_UNVERIFIED = re.compile(
    r"\b(?:no (?:tests?|backtests?|results?|evidence)"
    r"|not (?:been\s+)?(?:tested|verified|backtested)"
    r"|never (?:tested|backtested)|"
    r"without (?:test|evidence)|no completed trials)\b",
    re.I,
)

_FOLLOWUP = re.compile(
    r"\b(?:second one|first one|that one|the other|"
    r"what about|and those|same strategy|"
    r"continue|as before|that result)\b",
    re.I,
)

@dataclass(frozen=True)
class ConversationEvidenceState:
    history_turns: int
    user_correction_present: bool
    prior_assistant_metric_claim: bool
    explicit_missing_evidence: bool
    unresolved_reference: bool

def build_evidence_state(history, current_message):
    if not isinstance(history, (list, tuple)):
        history = ()

    selected = history[-12:]
    turns = 0
    correction = False
    claim = False
    no_evidence = False

    for item in selected:
        if isinstance(item, dict):
            role = item.get("role")
            content = item.get("content")
        else:
            role = getattr(item, "role", None)
            content = getattr(item, "content", None)

        if not isinstance(role, str) or not isinstance(content, str):
            continue

        role = role.casefold()
        if role not in ("user", "assistant"):
            continue

        turns += 1
        content = content[:1200]

        if role == "user":
            correction |= bool(_CORRECTION.search(content))
            no_evidence |= bool(_UNVERIFIED.search(content))

        if role == "assistant":
            claim |= bool(_ASSISTANT_METRIC.search(content))

    current = current_message if isinstance(current_message, str) else ""

    return ConversationEvidenceState(
        history_turns=turns,
        user_correction_present=correction,
        prior_assistant_metric_claim=claim,
        explicit_missing_evidence=no_evidence,
        unresolved_reference=bool(
            turns and _FOLLOWUP.search(current)
        ),
    )

def build_evidence_state_guidance(history, current_message):
    state = build_evidence_state(history, current_message)

    hints = []

    if state.user_correction_present:
        hints.append(
            "Keep earlier user corrections in scope unless the "
            "user explicitly changes them."
        )

    if state.prior_assistant_metric_claim:
        hints.append(
            "A previous assistant performance claim is not "
            "verified evidence by itself."
        )

    if state.explicit_missing_evidence:
        hints.append(
            "The conversation reports missing test evidence; "
            "do not manufacture results or certainty."
        )

    if state.unresolved_reference:
        hints.append(
            "Resolve references from available history; "
            "if ambiguous, say what remains uncertain."
        )

    # Only fixed instructions; never insert raw user content.

    # Preserve high-priority evidence and user
    # correction signals before response formatting.
    evidence = " ".join(hints)
    response = build_response_guidance(
        history, current_message
    )

    # Keep the combined state guidance compact
    # enough to coexist with 5H's existing hints.
    available = max(0, 285 - len(evidence))

    if evidence and available < 45:
        return evidence

    if len(response) <= available:
        return (
            (evidence + " " + response).strip()
            if evidence else response
        )

    # Never cut a policy sentence in half.
    short = (
        "Answer directly and concisely; do not "
        "ask for data before explaining what is known."
    )

    if len(short) <= available:
        return (
            (evidence + " " + short).strip()
            if evidence else short
        )

    return evidence

