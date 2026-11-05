
"""Bounded conversational response guidance.

No external access, persistent memory, or broker actions.
History is supplied by the existing authenticated chat path.
Only fixed policy phrases are returned, never raw user text.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_QUESTION = re.compile(
    r"\b(?:what|why|how|which|when|where|"
    r"explain|compare|difference|meaning)\b",
    re.I,
)

_FOLLOWUP = re.compile(
    r"\b(?:what about|and the|and what|"
    r"second one|first one|that one|those|"
    r"same one|continue|as before)\b",
    re.I,
)

_NUMERIC = re.compile(
    r"\b(?:exact|verified|measured|"
    r"win rate|drawdown|percentage|"
    r"how much|actual results|backtest)\b",
    re.I,
)

_EXPLANATION = re.compile(
    r"\b(?:what does|what is|explain|"
    r"how do|how does|difference|"
    r"realized|unrealized|losses|risk)\b",
    re.I,
)

_CORRECTION = re.compile(
    r"\b(?:no[,!]|i meant|actually[, ]|"
    r"instead of|not what i asked)\b",
    re.I,
)

@dataclass(frozen=True)
class ResponsePolicySignals:
    has_history: bool
    followup: bool
    explanation: bool
    numeric_evidence: bool
    correction: bool

def detect_response_signals(history, current_message):
    selected = (
        history[-12:]
        if isinstance(history, (list, tuple))
        else ()
    )

    valid = [
        x for x in selected
        if isinstance(x, dict)
        and x.get("role") in ("user", "assistant")
        and isinstance(x.get("content"), str)
    ]

    text = (
        current_message[:2000]
        if isinstance(current_message, str)
        else ""
    )

    return ResponsePolicySignals(
        has_history=bool(valid),
        followup=bool(_FOLLOWUP.search(text)),
        explanation=bool(
            _EXPLANATION.search(text)
            or _QUESTION.search(text)
        ),
        numeric_evidence=bool(_NUMERIC.search(text)),
        correction=bool(_CORRECTION.search(text)),
    )

def build_response_guidance(history, current_message):
    signals = detect_response_signals(
        history, current_message
    )

    # Keep this concise: 5I's helper enforces a
    # separate 520-character guidance budget.
    hints = []

    if signals.correction:
        hints.append(
            "Honor the latest user correction."
        )

    if signals.followup and signals.has_history:
        hints.append(
            "Answer the referenced subject directly."
        )

    if signals.explanation:
        hints.append(
            "Explain what is already knowable before "
            "asking for extra data."
        )

    if signals.numeric_evidence:
        hints.append(
            "Do not fabricate metrics; identify "
            "missing measurements briefly."
        )

    if not hints:
        hints.append(
            "Respond directly without unnecessary preamble."
        )

    hints.append(
        "Keep replies proportional; avoid repetitive "
        "lists and unnecessary clarification questions."
    )

    return " ".join(hints)
