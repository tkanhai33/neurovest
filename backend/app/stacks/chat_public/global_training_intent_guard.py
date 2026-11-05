
"""Pure global-training request classification.

This module does not authorize or execute training.
"""

from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class GlobalTrainingIntent:
    classification: str
    execution_requested: bool


_GLOBAL_SCOPE = re.compile(
    r"\b(?:global|system[\s-]*wide|system[\s-]*level)\b"
    r"(?:(?![.!?\n]).){0,100}?"
    r"\b(?:training|train|learning)\b"
    r"|"
    r"\b(?:training|train|learning)\b"
    r"(?:(?![.!?\n]).){0,100}?"
    r"\b(?:global|system[\s-]*wide|system[\s-]*level)\b",
    re.IGNORECASE,
)

_DIRECT_START = re.compile(
    r"^\s*(?:please\s+)?"
    r"(?:run|start|begin|launch|initiate|execute|kick\s+off)\b",
    re.IGNORECASE,
)

_NEGATED = re.compile(
    r"\b(?:do\s+not|don't|dont|never|without)\s+"
    r"(?:\w+\s+){0,4}?"
    r"(?:run|start|begin|launch|initiate|execute|train)\b",
    re.IGNORECASE,
)

_HYPOTHETICAL = re.compile(
    r"^\s*(?:can\s+you\s+explain|explain|what\s+if|"
    r"what\s+would|how\s+would|"
    r"what\s+happens|tell\s+me\s+about|"
    r"describe|why|how\s+does)\b",
    re.IGNORECASE,
)


def classify_global_training_request(
    message: str,
) -> GlobalTrainingIntent:
    """Return classification only; never grant permissions."""

    text = str(message or "").strip()

    if not _GLOBAL_SCOPE.search(text):
        return GlobalTrainingIntent(
            classification="not_global_training",
            execution_requested=False,
        )

    if _NEGATED.search(text):
        return GlobalTrainingIntent(
            classification="negated_global_training",
            execution_requested=False,
        )

    if _HYPOTHETICAL.search(text):
        return GlobalTrainingIntent(
            classification="global_training_discussion",
            execution_requested=False,
        )

    if _DIRECT_START.search(text):
        return GlobalTrainingIntent(
            classification="global_training_execution_request",
            execution_requested=True,
        )

    return GlobalTrainingIntent(
        classification="ambiguous_global_training",
        execution_requested=False,
    )


# NEUROVEST_GLOBAL_TRAINING_CHAT_BOUNDARY_V1
def global_training_chat_reply(
    message: str,
    *,
    developer_context_allowed: bool,
) -> str | None:
    """Explain restricted global training without executing it.

    developer_context_allowed indicates an authenticated developer
    context overlay, NOT authorization to launch global training.
    """

    result = classify_global_training_request(message)

    if not result.execution_requested:
        return None

    if not developer_context_allowed:
        return (
            "System-wide training is restricted to authorized "
            "NeuroVest developer operations. Your current account "
            "cannot initiate global training through chat. "
            "Personal training remains isolated from the global "
            "strategy profile. No training was started."
        )

    return (
        "I recognize your request for system-wide training. "
        "Developer context access does not by itself authorize "
        "global training execution. An approved global-training "
        "launcher and its governance checks must independently "
        "authorize the operation. This chat command does not "
        "execute global training. No training was started."
    )
