
"""Authoritative response for supported, verified logic.

Unsupported inputs return None so ordinary chat continues.
No LLM or external I/O. No authorization changes.
"""

from __future__ import annotations


def authoritative_reply(message, evaluate, verify):
    if not isinstance(message, str):
        return None

    # Extraction and verification must both succeed.
    evidence = evaluate(message, verify)

    if not isinstance(evidence, dict):
        return None

    if (
        evidence.get("status") != "not_entailed"
        or evidence.get("rule")
        != "universal_without_existential_import"
    ):
        return None

    return (
        "No. The conclusion does not necessarily follow. "
        "The premises describe universal relationships "
        "but do not establish that any members of the "
        "relevant categories exist. Those categories "
        "could be empty while all the premises remain "
        "true, making the proposed existential conclusion "
        "false."
    )


def finalize_reply(
    message,
    model_reply,
    evaluate,
    verify,
):
    """Preserve verified truth over a conflicting model answer.

    Return (response, source). Never call the model here.
    """
    deterministic = authoritative_reply(
        message, evaluate, verify
    )

    if deterministic is not None:
        return deterministic, "deterministic_verified"

    return model_reply, "model_unchanged"
