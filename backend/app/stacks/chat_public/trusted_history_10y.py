"""NeuroVest 10Y-R1: independently owner-checked history retrieval.

No prompt text is used as evidence of identity.
No database mutation or broker operation is performed.
Unverifiable records are rejected rather than stamped as trusted.
"""
from __future__ import annotations

from typing import Any


def _field(item: Any, name: str) -> Any:
    if isinstance(item, dict):
        return item.get(name)
    return getattr(item, name, None)


async def load_trusted_financial_history(
    *,
    store: Any,
    owner_user_id: str,
    thread_id: str,
    current_message_id: Any,
) -> tuple[Any, ...]:
    if (
        not isinstance(owner_user_id, str)
        or not owner_user_id.strip()
        or not isinstance(thread_id, str)
        or not thread_id.strip()
        or current_message_id is None
    ):
        return ()

    # A separate bounded, explicitly owner-scoped retrieval.
    # The general-purpose recent_messages projection stays untouched.
    try:
        bundle = await store.load_context_bundle(
            thread_id,
            message_limit=16,
            memory_limit=0,
            evidence_limit=0,
            owner_user_id=owner_user_id,
        )
    except Exception:
        return ()

    if not isinstance(bundle, dict):
        return ()

    # NEUROVEST_11A_VERIFIED_THREAD_OWNER
    state = bundle.get("conversation_state")
    state_owner = _field(state, "user_id")
    if state_owner is None:
        state_owner = _field(state, "owner_user_id")
    state_thread = _field(state, "thread_id")

    # NEUROVEST_11K_VERIFIED_THREAD_OWNER
    # The real ConversationState has thread_id but no user_id.
    # The server-loaded ChatThread carries the authenticated owner.
    # Require the returned thread AND state to agree with the
    # requested thread before trusting ownerless message records.
    server_thread = bundle.get("thread")
    server_thread_owner = _field(server_thread, "user_id")
    server_thread_id = _field(server_thread, "thread_id")

    server_thread_verified = (
        server_thread_owner is not None
        and server_thread_id is not None
        and str(server_thread_owner) == owner_user_id
        and str(server_thread_id) == thread_id
        and state_thread is not None
        and str(state_thread) == thread_id
        # An explicitly contradictory state owner is never ignored.
        and (
            state_owner is None
            or str(state_owner) == owner_user_id
        )
    )

    state_verified = (
        state_owner is not None
        and state_thread is not None
        and str(state_owner) == owner_user_id
        and str(state_thread) == thread_id
    ) or server_thread_verified

    messages = bundle.get("messages")
    if not isinstance(messages, (tuple, list)):
        return ()

    if len(messages) > 16:
        return ()

    result = []
    current_seen = False

    for message in messages:
        role = _field(message, "role")
        if not isinstance(role, str):
            continue

        if role.casefold() != "user":
            continue

        record_owner = _field(message, "user_id")
        if record_owner is None:
            record_owner = _field(message, "owner_user_id")

        record_thread = _field(message, "thread_id")
        record_id = _field(message, "message_id")
        content = _field(message, "content")

        # There is no implicit identity or trusted fallback.
        # An explicit message owner must always match.
        # A missing message owner is permitted only when
        # the server-returned conversation state verifies
        # both owner and thread.
        if (
            (
                record_owner is None
                and not state_verified
            )
            or (
                record_owner is not None
                and str(record_owner) != owner_user_id
            )
            or record_thread is None
            or str(record_thread) != thread_id
            or record_id is None
        ):
            return ()

        # The current message was persisted before assembly.
        # Exclude it and anything following it.
        if str(record_id) == str(current_message_id):
            current_seen = True
            break

        if not isinstance(content, str):
            continue

        if len(content) > 1500:
            continue

        # Normalize only a server-loaded record after
        # validating its identity and thread boundaries.
        # Never mutate persistence models.
        if record_owner is None:
            result.append({
                "role": role,
                "content": content,
                "user_id": owner_user_id,
                "thread_id": thread_id,
                "message_id": record_id,
            })
        else:
            result.append(message)

    if not current_seen:
        return ()

    return tuple(result[-8:])
