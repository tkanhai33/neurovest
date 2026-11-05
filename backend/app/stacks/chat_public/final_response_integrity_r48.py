"""R48 final mathematical integrity gate.

Preserves existing application verification and authority.
No broker, database, network, or user identity access.
"""
from __future__ import annotations

from typing import Any

from backend.app.stacks.chat_public.answer_quality_r44 import (
    math_findings,
)

VERSION = "NEUROVEST_G43_R48_FINAL_INTEGRITY"


def finalize(
    content: str,
    verification_result: Any,
    *,
    verifier: Any,
    math_bundle: Any,
    retrieval_bundle: Any,
    protected_developer: bool = False,
    enabled: bool = False,
):
    if not enabled or protected_developer:
        return content, verification_result

    if not isinstance(content, str):
        raise RuntimeError("R48: final response is not text")

    if not content.strip():
        raise RuntimeError("R48: empty final response")

    findings = math_findings(content)

    # Leave unrelated conversations and previously verified
    # content untouched; avoid duplicating model/tool work.
    if not findings:
        return content, verification_result

    checked = verifier(
        content,
        math_bundle=math_bundle,
        retrieval_bundle=retrieval_bundle,
    )

    final = getattr(checked, "final_response", None)

    if not isinstance(final, str) or not final.strip():
        raise RuntimeError(
            "R48: verifier returned an invalid final response"
        )

    # Never accept a purported correction containing the
    # same demonstrably incorrect mathematical claims.
    if math_findings(final):
        raise RuntimeError(
            "R48: incorrect mathematics survived verification"
        )

    if not (
        getattr(checked, "passed", False)
        or getattr(checked, "repaired", False)
    ):
        raise RuntimeError(
            "R48: final response was not accepted by verifier"
        )

    return final, checked
