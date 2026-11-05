"""V43 deterministic explanatory guard; no execution-stack imports."""
from __future__ import annotations

import re

from backend.app.stacks.chat_public.execution_state_projection_v26 import (
    MODES,
    render_execution_state,
)

_ISSUER = object()

class CapabilityEvidence:
    __slots__ = ("_text", "_mode", "_issuer")

    def __init__(self, text: str, mode: str | None, issuer: object):
        if issuer is not _ISSUER:
            raise ValueError("CapabilityEvidence requires internal issuance")
        self._text = text
        self._mode = mode
        self._issuer = issuer

    @property
    def text(self) -> str:
        return self._text

    @property
    def mode(self) -> str | None:
        return self._mode

def issue_capability_evidence(snapshot: object) -> CapabilityEvidence:
    """Only the server API should call this with its provider snapshot."""
    text = render_execution_state(snapshot)
    mode = None

    if isinstance(snapshot, dict):
        candidate = snapshot.get("mode")
        if (
            type(candidate) is str
            and candidate in MODES
            and "verification=SERVER_SNAPSHOT_VALIDATED\n" in text
            and f"operating_mode={candidate}\n" in text
        ):
            mode = candidate

    return CapabilityEvidence(text, mode, _ISSUER)

def validated_evidence_text(evidence: object) -> str | None:
    """Expose evidence text only after validating its complete structure."""
    if not _valid(evidence):
        return None
    return evidence.text


def _valid(evidence: object) -> bool:
    if not isinstance(evidence, CapabilityEvidence):
        return False
    if evidence._issuer is not _ISSUER:
        return False

    if evidence.mode is None:
        return evidence.text == render_execution_state(None)

    mode = evidence.mode
    if mode not in MODES:
        return False

    paper, emergency = MODES[mode]
    expected = render_execution_state({
        "mode": mode,
        "paper_execution_enabled": paper,
        "live_execution_enabled": False,
        "emergency_stop_active": emergency,
    })
    return evidence.text == expected

_DIRECT = re.compile(
    r"\b(?:neurovest|neuro)\b.*\b(?:support|allow|"
    r"available|enabled|disabled|can|could)\b.*"
    r"\bpaper\s+trad(?:e|es|ing)\b"
    r"|"
    r"\b(?:does|can|is)\s+(?:neurovest|neuro)\b.*"
    r"\bpaper\s+trad(?:e|es|ing)\b",
    re.IGNORECASE | re.DOTALL,
)

def deterministic_capability_answer(
    question: str,
    evidence: object,
) -> str | None:
    if not _valid(evidence):
        return None

    normalized = " ".join(str(question).split())
    if (
        not normalized.endswith("?")
        or len(normalized) > 250
        or not _DIRECT.search(normalized)
    ):
        return None

    if evidence.mode is None:
        return (
            "NeuroVest supports paper trading as a platform capability. "
            "The current execution-controller state could not be verified, "
            "so paper-order permission must not be assumed. "
            "Live broker execution is not approved. "
            "This explanation does not authorize or place an order."
        )

    mode = evidence.mode

    if mode == "SIMULATION":
        permission = (
            "The controller permits paper execution in SIMULATION mode, "
            "subject to authorization, risk, and governance checks."
        )
    else:
        permission = (
            f"The controller blocks paper execution in {mode} mode."
        )

    return (
        "NeuroVest supports paper trading as a platform capability. "
        + permission
        + " Live broker execution is not approved. "
        + "This explanation does not authorize or place an order."
    )
