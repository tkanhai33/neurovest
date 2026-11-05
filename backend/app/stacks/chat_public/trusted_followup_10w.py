"""10W-R1: server-record-based financial follow-up evidence.

Only callable with records passed from the authenticated,
owner-scoped context assembler. Prompt text never acts
as an authorization token.
"""
from __future__ import annotations

import json
from collections.abc import Sequence

from backend.app.stacks.chat_public.conversational_followup_10v import (
    BEGIN,
    END,
    resolve_followup_risk,
)

def _field(record, name):
    if isinstance(record, dict):
        return record.get(name)
    return getattr(record, name, None)

def trusted_followup_evidence(
    *,
    owner_user_id,
    thread_id,
    records,
    current_message,
    current_message_id,
):
    if not isinstance(owner_user_id, str) or not owner_user_id.strip():
        return ""
    if not isinstance(thread_id, str) or not thread_id.strip():
        return ""
    if not isinstance(current_message, str):
        return ""
    if not isinstance(records, (list, tuple)):
        return ""
    if len(records) > 40:
        return ""

    historical = []
    for record in records:
        role = _field(record, "role")
        if not isinstance(role, str) or role.lower() != "user":
            continue

        record_owner = _field(record, "user_id")
        if record_owner is None:
            record_owner = _field(record, "owner_user_id")
        if record_owner is None or str(record_owner) != owner_user_id:
            return ""

        record_thread = _field(record, "thread_id")
        if record_thread is None or str(record_thread) != thread_id:
            return ""

        record_id = _field(record, "message_id")
        if (
            current_message_id is not None
            and record_id is not None
            and str(record_id) == str(current_message_id)
        ):
            continue

        content = _field(record, "content")
        if not isinstance(content, str):
            continue

        # Exclude the current message even when a projected
        # record does not expose message_id.
        if content.strip() == current_message.strip():
            continue

        # Never allow a user message to inject structural
        # delimiters or another synthetic USER line.
        if (
            not content.strip()
            or len(content) > 1500
            or "\n" in content
            or "\r" in content
            or BEGIN in content
            or END in content
            or "[NEUROVEST_" in content
        ):
            continue

        historical.append(content.strip())

    if not historical:
        return ""

    # The assembler is expected to provide chronological
    # records. Never derive ordering from prompt text.
    historical = historical[-8:]

    context = (
        BEGIN + "\n"
        + "\n".join("USER: " + value for value in historical)
        + "\n" + END
    )

    result = resolve_followup_risk(
        context,
        current_message,
    )
    if result is None:
        return ""

    payload = {
        "type": "authenticated_history_risk_followup",
        "account_value": str(result.account_value),
        "risk_percent": str(result.risk_percent),
        "risk_budget": str(result.risk_budget),
        "account_verified": False,
        "buying_power_checked": False,
        "orders_placed": False,
        "position_size_calculated": False,
        "source": "server_assembled_user_records",
    }

    return (
        "\n\n[NEUROVEST_TRUSTED_FOLLOWUP_10W_R1]\n"
        + json.dumps(payload, sort_keys=True, separators=(",", ":"))
        + "\n[/NEUROVEST_TRUSTED_FOLLOWUP_10W_R1]\n"
        + "Use this only as hypothetical arithmetic on "
        + "user-provided inputs. Explain naturally. "
        + "Never imply account verification, position sizing, "
        + "broker execution, or permission to trade."
    )
