from fastapi import HTTPException
"""
134B4_CHAT_API_THREAD_WIRING

Thread-aware chat API transport with Stage 8E runtime trace
correlation.
"""

from fastapi import APIRouter, Depends, Request

from backend.app.core.runtime_trace import (
    create_trace_id,
    emit_runtime_step,
)

from backend.app.stacks.chat_public.public_controls import (
    enforce_public_chat_controls,
)

from backend.app.stacks.chat_public.chat_runtime import (
    run_chat_turn,
)

from backend.app.stacks.identity_auth.contracts import (
    AuthenticatedPrincipal,
)

from backend.app.stacks.identity_auth.api_dependencies import (
    require_authenticated_principal,
)

from backend.app.stacks.chat_public.contracts import (
    ChatRequest,
)


router = APIRouter()


# NEUROVEST_SSE_VERIFICATION_METADATA_BOUNDARY_V1
def _public_chat_message_metadata(metadata: object) -> dict:
    """Return owner-visible message metadata without internal verification.

    Full diagnostic metadata remains in persistent storage and is not
    modified by this transport-layer projection.
    """
    if not isinstance(metadata, dict):
        return {}

    public = dict(metadata)
    public.pop("response_verification", None)

    return public





@router.post("/api/v1/chat")
@enforce_public_chat_controls(
    payload_argument="payload",
)
async def chat_endpoint(
    payload: ChatRequest,
    request: Request,
    principal: AuthenticatedPrincipal = Depends(
        require_authenticated_principal
    ),
):
    trace_id = str(
        getattr(
            request.state,
            "runtime_trace_id",
            "",
        )
        or create_trace_id(
            "chat"
        )
    )

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="CHAT_API_ACCEPTED",
        node="chat_api",
        source="http_api",
        destination="chat_api",
        status="active",
        layer="L5",
        stack="chat_public",
        details={
            "operation": "chat_turn",
            "payload_bytes": len(
                payload.message.encode(
                    "utf-8"
                )
            ),
        },
    )

    # NEUROVEST_V26_TRUSTED_API_HANDOFF
    # Never accept operating-state data from the client payload.
    import os as _v26_os
    evidence_kwargs = {}

    if _v26_os.getenv(
        "NEUROVEST_CHAT_EXECUTION_EVIDENCE_V1", "0"
    ).strip() == "1":
        from backend.app.stacks.chat_public.execution_capability_guard_v43 import (
            issue_capability_evidence,
        )

        snapshot = None
        try:
            provider = getattr(
                request.app.state,
                "neurovest_execution_snapshot_provider",
                None,
            )
            if callable(provider):
                snapshot = provider()
        except Exception:
            snapshot = None

        evidence_kwargs["trusted_execution_evidence"] = (
            issue_capability_evidence(snapshot)
        )

    try:
        result = await run_chat_turn(
            payload,
            runtime_trace_id=trace_id,
            principal=principal,
            **evidence_kwargs,
        )
    except PermissionError:
        raise HTTPException(
            status_code=404,
            detail="Chat thread not found.",
        ) from None

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="CHAT_API_RESPONSE_READY",
        node="chat_api",
        source="chat_runtime",
        destination="chat_api",
        status=(
            "completed"
            if result.get("status")
            == "ok"
            else str(
                result.get(
                    "status",
                    "failed",
                )
            )
        ),
        layer="L5",
        stack="chat_public",
        details={
            "operation": "chat_turn",
            "response_bytes": len(
                str(
                    result.get(
                        "message",
                        "",
                    )
                ).encode(
                    "utf-8"
                )
            ),
            "success": (
                result.get("status")
                == "ok"
            ),
        },
    )

    return result


# NEUROVEST_TRAINING_CONVERSATION_V1
# Server-sent conversation synchronization.
# Persisted PostgreSQL messages remain the source of truth.

import asyncio as _stream_asyncio
import json as _stream_json
from fastapi.responses import StreamingResponse as _StreamResponse

from backend.app.stacks.chat_public.chat_runtime import (
    conversation_store as _stream_store,
)


@router.get("/api/v1/chat/threads/{thread_id}/events")
async def authenticated_chat_events(
    thread_id: str,
    request: Request,
    principal: AuthenticatedPrincipal = Depends(
        require_authenticated_principal
    ),
):
    owner = str(
        getattr(principal, "subject", "") or ""
    ).strip()

    if not owner:
        raise HTTPException(
            status_code=401,
            detail="Authenticated owner required.",
        )

    thread = await _stream_store.require_thread(thread_id)

    if str(getattr(thread, "user_id", "") or "") != owner:
        raise HTTPException(
            status_code=404,
            detail="Chat thread not found.",
        )

    async def events():
        seen = set()
        bootstrapped = False
        heartbeat = 0

        while not await request.is_disconnected():
            # Recheck ownership on each cycle. A thread must
            # never become accessible merely because an SSE
            # connection was previously authorized.
            current = await _stream_store.require_thread(
                thread_id
            )

            if str(getattr(current, "user_id", "") or "") != owner:
                break

            # Select recent messages, then restore chronological order.
            messages = await _stream_store.list_messages(
                thread_id,
                limit=100,
                oldest_first=False,
            )
            messages = list(reversed(messages))

            if not bootstrapped:
                # Replay recent history to a newly connected browser.
                messages = messages[-50:]
                bootstrapped = True

            for item in messages:
                message_id = str(item.message_id)

                if message_id in seen:
                    continue

                seen.add(message_id)

                payload = {
                    "message_id": message_id,
                    "thread_id": thread_id,
                    "role": item.role,
                    "content": item.content,
                    "created_at": str(item.created_at),
                    "intent": item.intent,
                    "metadata": _public_chat_message_metadata(item.metadata),
                }

                yield (
                    "id: " + message_id + "\n"
                    + "event: chat_message\n"
                    + "data: "
                    + _stream_json.dumps(
                        payload,
                        default=str,
                        ensure_ascii=False,
                    )
                    + "\n\n"
                )

            # Bound the reconciliation cache.
            if len(seen) > 2000:
                seen = {
                    str(item.message_id)
                    for item in messages
                }

            heartbeat += 1

            if heartbeat % 10 == 0:
                yield ": heartbeat\n\n"

            await _stream_asyncio.sleep(2)

    return _StreamResponse(
        events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
        },
    )


# NEUROVEST_CHAT_HISTORY_GET_V1
@router.get("/api/v1/chat/threads/{thread_id}/messages")
async def authenticated_chat_messages(
    thread_id: str,
    principal: AuthenticatedPrincipal = Depends(
        require_authenticated_principal
    ),
):
    owner = str(getattr(principal, "subject", "") or "").strip()
    if not owner:
        raise HTTPException(
            status_code=401,
            detail="Authenticated owner required.",
        )

    thread = await _stream_store.require_thread(thread_id)
    if str(getattr(thread, "user_id", "") or "") != owner:
        raise HTTPException(
            status_code=404,
            detail="Chat thread not found.",
        )

    messages = await _stream_store.list_messages(
        thread_id,
        limit=500,
        oldest_first=False,
    )
    messages = list(reversed(messages))

    return {
        "thread_id": thread_id,
        "messages": [
            {
                "message_id": str(item.message_id),
                "role": item.role,
                "content": item.content,
                "created_at": str(item.created_at),
            }
            for item in messages
            if item.role in {"user", "assistant"}
        ],
    }
