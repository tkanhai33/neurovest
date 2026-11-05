from __future__ import annotations

import hashlib
import logging
from typing import Any

from backend.app.stacks.chat_public.developer_intelligence_3e import (
    is_improvement_request,
)

VERSION = "NEURO_DEVELOPER_EXECUTION_TRACE_3ER4"

LOGGER = logging.getLogger(
    "neurovest.developer_execution_trace"
)

STAGES = frozenset({
    "IDEMPOTENT_REPLAY",
    "ROUTE_DECISION",
    "AWARENESS_ENTERED",
    "VERIFIED_REPORT_SELECTED",
    "AWARENESS_RESULT",
    "PRE_PERSISTENCE",
    "PERSISTED",
})


def fingerprint(value: Any) -> str:
    """Fingerprint response text without logging the text."""
    if not isinstance(value, str):
        return "not_text"

    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()[:16]


def emit(
    *,
    question: str,
    stage: str,
    trace_id: str = "",
    **flags: Any,
) -> bool:
    """
    Only trace recognized developer self-assessment
    questions. No tokens, roles, claims, message content,
    request bodies or raw evidence are logged.
    """
    if not is_improvement_request(question):
        return False

    if stage not in STAGES:
        return False

    fields = []

    for key, value in sorted(flags.items()):
        if not key.replace("_", "").isalnum():
            continue

        if isinstance(value, bool):
            safe = "true" if value else "false"
        elif value is None:
            safe = "none"
        elif isinstance(value, int) and 0 <= value <= 1000000:
            safe = str(value)
        else:
            continue

        fields.append(f"{key}={safe}")

    # Runtime trace IDs are internal correlation labels.
    # Sanitize them before logging.
    safe_trace = "".join(
        c for c in str(trace_id)
        if c.isalnum() or c in "-_"
    )[:80] or "unknown"

    LOGGER.warning(
        "NV3ER4 stage=%s trace=%s %s",
        stage,
        safe_trace,
        " ".join(fields),
    )

    return True
