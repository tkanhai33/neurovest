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

    result = await run_chat_turn(
        payload,
        runtime_trace_id=trace_id,
        principal=principal,
    )

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
