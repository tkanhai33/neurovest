"""
134B4_CHAT_API_THREAD_WIRING

Connects the existing NeuroVest chat runtime to the persistent
conversation store introduced in Phase 134B3.

This phase:
- creates or resumes chat threads
- persists user messages
- persists assistant messages
- preserves parent-message relationships
- returns thread and message identifiers
- prevents duplicate assistant generation for retried client messages

This phase does not:
- inject historical context into Ollama
- summarize conversations
- extract durable memory automatically
- enable streaming
- execute new financial tools
- alter broker or live-trading state
"""

from __future__ import annotations

import re

from typing import Any
from time import perf_counter

from backend.app.core.runtime_trace import (
    create_trace_id,
    emit_runtime_step,
)

from backend.app.stacks.strategy_candidate_sandbox.L4_runtime_orchestration.bounded_training_runtime import (
    start_bounded_training_session,
)

from backend.app.stacks.chat_public.chat_intent_regex import (
    detect_chat_intent,
)
from backend.app.stacks.chat_public.cognitive_model_router import (
    CognitiveRoutingDecision,
    route_cognitive_request,
)
from backend.app.stacks.chat_public.developer_response_builder import (
    build_developer_response,
)
from backend.app.stacks.chat_public.contracts import (
    ChatRequest,
    ChatResponse,
    ToolEvidence,
)
from backend.app.stacks.chat_public.conversation_service import (
    conversation_store,
)
from backend.app.stacks.chat_public.context import (
    CONTEXT_VERSION,
    assemble_chat_context,
    update_summary_memory,
)
from backend.app.stacks.chat_public.role_overlay_registry import (
    render_role_overlay,
    resolve_principal_overlay,
    resolve_role_overlay,

)

from backend.app.stacks.chat_public.ollama_chat_client import (
    ask_ollama,
    resolve_runtime_model,
)
from backend.app.stacks.chat_public.rag.live_retrieval import (
    LiveRetrievalBundle,
    retrieve_live_evidence,
)
from backend.app.stacks.chat_public.math_tools.live_math import (
    LiveMathBundle,
    evaluate_live_math,
)
from backend.app.stacks.chat_public.response_verification import (
    ResponseVerificationResult,
    verify_response,
)
from backend.app.stacks.chat_public.strategy_proposal_capture import (
    capture_strategy_proposal,
)


OLLAMA_PROVIDER = "ollama"


def _response_message(
    response: dict[str, Any],
) -> str:
    response_type = str(
        response.get("type") or "text"
    )

    if response_type == "text":
        return str(
            response.get("message") or ""
        )

    command = str(
        response.get("command") or response_type
    )

    symbol = response.get("symbol")

    if symbol:
        return (
            f"Command prepared: {command} "
            f"for {symbol}."
        )

    return f"Command prepared: {command}."


def _ensure_approved_retrieval_citation(
    response: str,
    citations: Any,
) -> str:
    normalized = str(
        response
    ).strip()

    approved_tokens = [
        str(
            citation.get(
                "citation",
                "",
            )
        ).strip()
        for citation in citations
        if isinstance(
            citation,
            dict,
        )
        and str(
            citation.get(
                "citation",
                "",
            )
        ).strip()
    ]

    if not approved_tokens:
        return normalized

    if any(
        token in normalized
        for token in approved_tokens
    ):
        return normalized

    return (
        normalized
        + "\n\n"
        + "Approved local research source: "
        + approved_tokens[0]
    )



def _chat_training_role(
    principal: Any | None,
) -> str:
    if principal is None:
        return ""

    direct = (
        getattr(
            principal,
            "role",
            None,
        )
        or getattr(
            principal,
            "authorization_role",
            None,
        )
    )

    if direct:
        return str(
            direct
        ).strip().lower()

    claims = getattr(
        principal,
        "claims",
        {},
    )

    if not isinstance(
        claims,
        dict,
    ):
        claims = {}

    return str(
        claims.get(
            "authorization_role"
        )
        or claims.get("role")
        or ""
    ).strip().lower()


def _chat_training_subject(
    principal: Any | None,
) -> str:
    if principal is None:
        return ""

    direct = (
        getattr(
            principal,
            "subject",
            None,
        )
        or getattr(
            principal,
            "user_id",
            None,
        )
    )

    if direct:
        return str(
            direct
        ).strip()

    claims = getattr(
        principal,
        "claims",
        {},
    )

    if not isinstance(
        claims,
        dict,
    ):
        claims = {}

    return str(
        claims.get("sub")
        or claims.get("user_id")
        or ""
    ).strip()


def _chat_training_session(
    principal: Any | None,
) -> str:
    if principal is None:
        return ""

    direct = (
        getattr(
            principal,
            "session_id",
            None,
        )
        or getattr(
            principal,
            "token_family_id",
            None,
        )
        or getattr(
            principal,
            "token_id",
            None,
        )
    )

    if direct:
        return str(
            direct
        ).strip()

    claims = getattr(
        principal,
        "claims",
        {},
    )

    if not isinstance(
        claims,
        dict,
    ):
        claims = {}

    return str(
        claims.get("session_id")
        or claims.get("session_family_id")
        or claims.get("family_id")
        or claims.get("sid")
        or claims.get("jti")
        or ""
    ).strip()


def _blocked_training_chat_response(
    *,
    intent,
    message: str,
    reason: str,
) -> dict[str, Any]:
    return {
        "status": "blocked",
        "response": {
            "type": "text",
            "message": message,
        },
        "intent": intent.intent,
        "symbol": None,
        "training_run": None,
        "provider": None,
        "model": None,
        "tool_truth_state":
            "deterministic_policy",
        "error": reason,
        "cognitive_route": None,
    }

def handle_chat_message(
    message: str,
    *,
    model_input: str | None = None,
    detected_intent: Any | None = None,
    developer_evidence_allowed: bool = False,
    routing_decision: CognitiveRoutingDecision | None = None,
    principal: Any | None = None,
) -> dict[str, Any]:
    """
    Preserve the existing intent and Ollama behavior.

    Persistence is intentionally handled by run_chat_turn so this
    synchronous decision function remains focused on chat behavior.
    """

    intent = (
        detected_intent
        if detected_intent is not None
        else detect_chat_intent(
            message
        )
    )

    if intent.blocked:
        return {
            "status": "blocked",
            "response": {
                "type": "text",
                "message": (
                    "Live execution is locked. I can discuss "
                    "the plan, risk, and simulation, but I "
                    "cannot place real trades from chat."
                ),
            },
            "intent": intent.intent,
            "symbol": intent.symbol,
            "provider": None,
            "model": None,
            "tool_truth_state": "not_required",
        }


    if intent.intent == "run_training_session":
        duration_seconds = 120

        duration_match = re.search(
            r"\b(\d{1,3})\s*"
            r"(second|seconds|minute|minutes)\b",
            message,
            re.IGNORECASE,
        )

        if duration_match:
            amount = int(
                duration_match.group(1)
            )

            unit = (
                duration_match.group(2)
                .lower()
            )

            duration_seconds = (
                amount * 60
                if unit.startswith(
                    "minute"
                )
                else amount
            )

        duration_seconds = max(
            1,
            min(
                duration_seconds,
                600,
            ),
        )

        role = _chat_training_role(
            principal
        )

        subject = _chat_training_subject(
            principal
        )

        session_id = _chat_training_session(
            principal
        )

        if not subject:
            return _blocked_training_chat_response(
                intent=intent,
                message=(
                    "Training could not start because "
                    "the authenticated account identity "
                    "was unavailable."
                ),
                reason=(
                    "authenticated_training_subject_missing"
                ),
            )

        if role in {
            "admin",
            "administrator",
            "system_admin",
            "support",
        }:
            return _blocked_training_chat_response(
                intent=intent,
                message=(
                    "Administrators may inspect training "
                    "health and failures, but cannot start "
                    "training sessions. System-wide "
                    "training is restricted to the "
                    "Developer role."
                ),
                reason=(
                    "administrator_training_start_denied"
                ),
            )

        if role in {
            "developer",
            "dev",
            "owner",
        }:
            training = (
                start_bounded_training_session(
                    duration_seconds=(
                        duration_seconds
                    ),
                    universe="canada",
                    requested_by=subject,
                    source=(
                        "authenticated_developer_chat"
                    ),
                    scope="system",
                    owner_user_id=None,
                    owner_session_id=None,
                    requested_by_role=role,
                )
            )

        else:
            if not session_id:
                return _blocked_training_chat_response(
                    intent=intent,
                    message=(
                        "Training could not start because "
                        "the authenticated session identity "
                        "was unavailable."
                    ),
                    reason=(
                        "authenticated_training_session_missing"
                    ),
                )

            training = (
                start_bounded_training_session(
                    duration_seconds=(
                        duration_seconds
                    ),
                    universe="canada",
                    requested_by=subject,
                    source=(
                        "authenticated_user_chat"
                    ),
                    scope="user",
                    owner_user_id=subject,
                    owner_session_id=session_id,
                    requested_by_role=(
                        role or "user"
                    ),
                )
            )

        run_id = str(
            training["run_id"]
        )

        return {
            "status": "ok",
            "response": {
                "type": "text",
                "message": (
                    "Bounded Canadian historical "
                    "training session started. "
                    f"Run ID: {run_id}. "
                    f"Planned duration: "
                    f"{training['duration_seconds']} "
                    "seconds. The session reads "
                    "repository historical CSV data "
                    "only. Trades, portfolio mutation, "
                    "strategy promotion, broker access, "
                    "and live execution remain disabled."
                ),
            },
            "intent": intent.intent,
            "symbol": None,
            "training_run": training,
            "provider": (
                "neurovest_bounded_"
                "training_runtime"
            ),
            "model": None,
            "tool_truth_state": "grounded",
            "error": None,
            "cognitive_route": None,
        }

    if intent.intent == "graph_reset":
        return {
            "status": "ok",
            "response": {
                "type": "direct_command",
                "command": "graph_reset",
            },
            "intent": intent.intent,
            "symbol": intent.symbol,
            "provider": None,
            "model": None,
            "tool_truth_state": "not_required",
        }

    if intent.intent == "graph_validate":
        return {
            "status": "ok",
            "response": {
                "type": "direct_command",
                "command": "graph_validate",
            },
            "intent": intent.intent,
            "symbol": intent.symbol,
            "provider": None,
            "model": None,
            "tool_truth_state": "not_required",
        }

    if intent.intent == "simulate_trade":
        return {
            "status": "ok",
            "response": {
                "type": "direct_command",
                "command": "simulate_trade",
                "symbol": intent.symbol,
            },
            "intent": intent.intent,
            "symbol": intent.symbol,
            "provider": None,
            "model": None,
            "tool_truth_state": "not_required",
        }

    use_deterministic_developer_evidence = (
        intent.developer_mode
        and developer_evidence_allowed
        and (
            intent.self_evaluation
            or intent.requires_repo_context
            or intent.requires_architecture_context
            or intent.subtype == "developer_review"
        )
    )

    if use_deterministic_developer_evidence:
        reply = build_developer_response(
            subtype=intent.subtype,
        )
        provider = "neurovest_local_evidence"
        model = None
        status = "ok"
        error = None
        tool_truth_state = "grounded"
    else:
        routing_decision = (
            routing_decision
            if routing_decision is not None
            else route_cognitive_request(
                message,
                intent=intent,
            )
        )

        try:
            reply = ask_ollama(
                model_input or message,
                intent=intent.intent,
                symbol=intent.symbol,
                model=routing_decision.model,
            )

            provider = OLLAMA_PROVIDER
            model = routing_decision.model
            status = "ok"
            error = None
            tool_truth_state = (
                "ungrounded"
                if routing_decision.retrieval_required
                else (
                    "deterministic_tool_required"
                    if routing_decision.deterministic_tool_required
                    else "ungrounded"
                )
            )

        except Exception as primary_exc:
            try:
                reply = ask_ollama(
                    model_input or message,
                    intent=intent.intent,
                    symbol=intent.symbol,
                    model=routing_decision.fallback_model,
                )

                provider = OLLAMA_PROVIDER
                model = routing_decision.fallback_model
                status = "ok"
                error = (
                    "Primary model failed; fallback used: "
                    f"{type(primary_exc).__name__}: "
                    f"{primary_exc}"
                )
                tool_truth_state = (
                    "fallback_ungrounded"
                )

            except Exception as fallback_exc:
                reply = (
                    "Neuro local model is unavailable: "
                    f"{type(fallback_exc).__name__}: "
                    f"{fallback_exc}"
                )

                provider = OLLAMA_PROVIDER
                model = routing_decision.fallback_model
                status = "error"
                error = (
                    "Primary model failure: "
                    f"{type(primary_exc).__name__}: "
                    f"{primary_exc}; fallback failure: "
                    f"{type(fallback_exc).__name__}: "
                    f"{fallback_exc}"
                )
                tool_truth_state = "ungrounded"

    strategy_capture = capture_strategy_proposal(
        str(message),
        str(reply),
        intent=intent.intent,
        symbol=intent.symbol,
    )

    return {
        "status": status,
        "response": {
            "type": "text",
            "message": str(reply),
        },
        "intent": intent.intent,
        "symbol": intent.symbol,
        "strategy_capture": strategy_capture,
        "provider": provider,
        "model": resolve_runtime_model(model),
        "tool_truth_state": tool_truth_state,
        "error": error,
        "cognitive_route": (
            routing_decision.as_dict()
            if not use_deterministic_developer_evidence
            else None
        ),
    }


async def _find_existing_assistant_reply(
    *,
    thread_id: str,
    user_message_id: str,
) -> Any | None:
    messages = await conversation_store.list_messages(
        thread_id,
        limit=500,
        oldest_first=True,
    )

    for message in messages:
        if (
            message.role == "assistant"
            and message.parent_message_id
            == user_message_id
        ):
            return message

    return None


async def run_chat_turn(
    message: str | dict[str, Any] | ChatRequest | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    principal = kwargs.pop("principal", None)

    trace_id = str(
        kwargs.pop(
            "runtime_trace_id",
            "",
        )
        or create_trace_id(
            "chat"
        )
    )

    turn_started = perf_counter()

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="CHAT_RUNTIME_STARTED",
        node="chat_runtime",
        source="chat_api",
        destination="chat_runtime",
        status="active",
        layer="L4",
        stack="chat_public",
        details={
            "operation": "run_chat_turn",
        },
    )

    if isinstance(message, ChatRequest):
        request = message

    elif isinstance(message, dict):
        request = ChatRequest.model_validate(
            message
        )

    else:
        raw_message = (
            message
            if message is not None
            else kwargs.get("message")
            or kwargs.get("content")
            or ""
        )

        request = ChatRequest(
            message=str(raw_message),
            thread_id=kwargs.get("thread_id"),
            parent_message_id=kwargs.get(
                "parent_message_id"
            ),
            client_message_id=kwargs.get(
                "client_message_id"
            ),
            stream=bool(
                kwargs.get("stream", False)
            ),
            metadata=dict(
                kwargs.get("metadata") or {}
            ),
        )

    persistence_started = perf_counter()

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="CONVERSATION_LOOKUP_STARTED",
        node="conversation_store",
        source="chat_runtime",
        destination="conversation_store",
        status="active",
        layer="L3",
        stack="chat_public",
        details={
            "operation": "get_or_create_thread",
        },
    )

    thread = await conversation_store.get_or_create_thread(
        thread_id=request.thread_id,
        title=(
            request.message[:80]
            if request.thread_id is None
            else None
        ),
        metadata={
            "created_by": "chat_api",
            "contract": "134A.v1",
        },
    )

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="POSTGRESQL_THREAD_READY",
        node="postgresql_adapter",
        source="conversation_store",
        destination="postgresql_adapter",
        status="completed",
        layer="L0",
        stack="db_runtime",
        details={
            "operation": "thread_lookup",
            "latency_ms": (
                perf_counter()
                - persistence_started
            ) * 1000,
            "success": True,
        },
    )

    existing_user_message = None

    if request.client_message_id:
        existing_user_message = (
            await conversation_store
            .get_message_by_client_id(
                thread_id=thread.thread_id,
                client_message_id=(
                    request.client_message_id
                ),
            )
        )

    user_persist_started = perf_counter()

    user_message = await conversation_store.append_message(
        thread_id=thread.thread_id,
        role="user",
        content=request.message,
        parent_message_id=(
            request.parent_message_id
        ),
        client_message_id=(
            request.client_message_id
        ),
        metadata={
            **request.metadata,
            "stream_requested": request.stream,
        },
    )

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="USER_MESSAGE_PERSISTED",
        node="conversation_persistence",
        source="postgresql_adapter",
        destination="conversation_persistence",
        status="completed",
        layer="L3",
        stack="chat_public",
        details={
            "operation": "append_user_message",
            "latency_ms": (
                perf_counter()
                - user_persist_started
            ) * 1000,
            "payload_bytes": len(
                request.message.encode(
                    "utf-8"
                )
            ),
            "success": True,
        },
    )

    if existing_user_message is not None:
        existing_assistant = (
            await _find_existing_assistant_reply(
                thread_id=thread.thread_id,
                user_message_id=(
                    user_message.message_id
                ),
            )
        )

        if existing_assistant is not None:
            state = (
                await conversation_store
                .get_conversation_state(
                    thread.thread_id
                )
            )

            response = ChatResponse(
                status="ok",
                thread_id=thread.thread_id,
                user_message_id=(
                    user_message.message_id
                ),
                assistant_message_id=(
                    existing_assistant.message_id
                ),
                message=existing_assistant.content,
                intent=existing_assistant.intent,
                symbol=existing_assistant.symbol,
                provider=existing_assistant.provider,
                model=existing_assistant.model,
                tool_truth_state="not_required",
                conversation_state=state,
                metadata={
                    "idempotent_replay": True,
                    "streaming_enabled": False,
                },
            )

            payload = response.model_dump(
                mode="json"
            )

            payload["response"] = {
                "type": "text",
                "message": (
                    existing_assistant.content
                ),
            }

            await emit_runtime_step(
                trace_id=trace_id,
                event_type="CHAT_IDEMPOTENT_REPLAY_COMPLETED",
                node="response_validation",
                source="conversation_store",
                destination="chat_api",
                status="completed",
                layer="L3",
                stack="chat_public",
                details={
                    "operation": "idempotent_replay",
                    "latency_ms": (
                        perf_counter()
                        - turn_started
                    ) * 1000,
                    "success": True,
                },
            )

            return payload

    context_started = perf_counter()

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="CONTEXT_ASSEMBLY_STARTED",
        node="context_assembler",
        source="conversation_persistence",
        destination="context_assembler",
        status="active",
        layer="L2",
        stack="chat_public",
        details={
            "operation": "assemble_chat_context",
        },
    )

    detected_intent = detect_chat_intent(
        request.message
    )

    resolved_role_overlay = (
        resolve_principal_overlay(
            principal
        )
        if principal is not None
        else resolve_role_overlay(
            role="user"
        )
    )

    developer_evidence_allowed = bool(
        resolved_role_overlay
        .role_overlay
        .may_receive_repository_context
    )

    role_overlay_text = (
        render_role_overlay(
            resolved_role_overlay
        )
    )

    routing_decision = route_cognitive_request(
        request.message,
        intent=detected_intent,
    )

    math_started = perf_counter()

    math_bundle: LiveMathBundle = (
        evaluate_live_math(
            request.message,
            requested=(
                routing_decision
                .deterministic_tool_required
            ),
        )
    )

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="DETERMINISTIC_MATH_COMPLETED",
        node="deterministic_math_engine",
        source="intent_classifier",
        destination="context_assembler",
        status=(
            "completed"
            if math_bundle.grounded
            else (
                "degraded"
                if math_bundle.requested
                else "not_required"
            )
        ),
        layer="L2",
        stack="chat_public",
        details={
            "operation":
                math_bundle.operation,
            "requested":
                math_bundle.requested,
            "extracted":
                math_bundle.extracted,
            "succeeded":
                math_bundle.succeeded,
            "latency_ms": (
                perf_counter()
                - math_started
            ) * 1000,
            "error":
                math_bundle.error,
        },
    )

    retrieval_started = perf_counter()

    retrieval_bundle: LiveRetrievalBundle = (
        retrieve_live_evidence(
            request.message,
            requested=(
                routing_decision
                .retrieval_required
            ),
        )
    )

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="KNOWLEDGE_RETRIEVAL_COMPLETED",
        node="local_knowledge_index",
        source="intent_classifier",
        destination="context_assembler",
        status=(
            "completed"
            if retrieval_bundle.error is None
            else "degraded"
        ),
        layer="L2",
        stack="chat_public",
        details={
            "operation":
                "retrieve_live_evidence",
            "requested":
                retrieval_bundle.requested,
            "grounded":
                retrieval_bundle.grounded,
            "result_count":
                len(
                    retrieval_bundle.results
                ),
            "latency_ms": (
                perf_counter()
                - retrieval_started
            ) * 1000,
            "error":
                retrieval_bundle.error,
        },
    )

    assembled_context = await assemble_chat_context(
        thread_id=thread.thread_id,
        current_message=request.message,
        intent_metadata={
            "intent": detected_intent.intent,
            "family": detected_intent.family,
            "subtype": detected_intent.subtype,
            "confidence": detected_intent.confidence,
            "developer_mode": (
                detected_intent.developer_mode
                and developer_evidence_allowed
            ),
            "architecture_mode": (
                detected_intent.architecture_mode
                and developer_evidence_allowed
            ),
            "self_evaluation": (
                detected_intent.self_evaluation
                and developer_evidence_allowed
            ),
            "requires_repo_context": (
                detected_intent.requires_repo_context
                and developer_evidence_allowed
            ),
            "requires_architecture_context": (
                detected_intent.requires_architecture_context
                and developer_evidence_allowed
            ),
        },
        role_overlay=role_overlay_text,
    )

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="MEMORY_CONTEXT_ASSEMBLED",
        node="memory_context",
        source="context_assembler",
        destination="memory_context",
        status="completed",
        layer="L2",
        stack="memory",
        details={
            "operation": "context_bundle",
            "latency_ms": (
                perf_counter()
                - context_started
            ) * 1000,
            "success": True,
        },
    )

    inference_started = perf_counter()

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="INTENT_CLASSIFICATION_STARTED",
        node="intent_classifier",
        source="memory_context",
        destination="intent_classifier",
        status="active",
        layer="L2",
        stack="chat_public",
        details={
            "operation": "detect_chat_intent",
        },
    )

    model_input = assembled_context.prompt

    if retrieval_bundle.prompt_section:
        model_input = (
            model_input
            + "\n\n"
            + retrieval_bundle.prompt_section
        )

    if (
        retrieval_bundle.grounded
        and retrieval_bundle.citations
    ):
        approved_citation_tokens = [
            str(
                citation.get(
                    "citation",
                    "",
                )
            ).strip()
            for citation
            in retrieval_bundle.citations
            if str(
                citation.get(
                    "citation",
                    "",
                )
            ).strip()
        ]

        if approved_citation_tokens:
            model_input = (
                model_input
                + "\n\n"
                + "MANDATORY CITATION CONTRACT:\n"
                + "Your final answer must contain at least one "
                + "approved citation token exactly as written below.\n"
                + "Do not replace these tokens with [1], footnote "
                + "numbers, author-year references, URLs, or invented "
                + "citations.\n"
                + "Only cite claims supported by the supplied local "
                + "research evidence.\n"
                + "Approved citation tokens:\n- "
                + "\n- ".join(
                    approved_citation_tokens
                )
            )

    if math_bundle.prompt_section:
        model_input = (
            model_input
            + "\n\n"
            + math_bundle.prompt_section
        )

    runtime_result = handle_chat_message(
        request.message,
        model_input=model_input,
        detected_intent=detected_intent,
        developer_evidence_allowed=(
            developer_evidence_allowed
        ),
        routing_decision=(
            routing_decision
        ),
        principal=principal,
    )

    if (
        retrieval_bundle.grounded
        or math_bundle.grounded
    ):
        runtime_result[
            "tool_truth_state"
        ] = "grounded"

    intent_status = str(
        runtime_result.get(
            "status",
            "error",
        )
    )

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="INTENT_CLASSIFICATION_COMPLETED",
        node="intent_classifier",
        source="intent_classifier",
        destination=(
            "ollama_adapter"
            if runtime_result.get(
                "provider"
            )
            == OLLAMA_PROVIDER
            else "response_validation"
        ),
        status=(
            "completed"
            if intent_status == "ok"
            else intent_status
        ),
        symbol=runtime_result.get(
            "symbol"
        ),
        layer="L2",
        stack="chat_public",
        details={
            "operation": (
                runtime_result.get(
                    "intent"
                )
                or "unknown"
            ),
            "success": (
                intent_status == "ok"
            ),
        },
    )

    if (
        runtime_result.get(
            "provider"
        )
        == OLLAMA_PROVIDER
    ):
        await emit_runtime_step(
            trace_id=trace_id,
            event_type="OLLAMA_RESPONSE_RECEIVED",
            node="ollama_adapter",
            source="intent_classifier",
            destination="ollama_adapter",
            status=(
                "completed"
                if intent_status == "ok"
                else "failed"
            ),
            symbol=runtime_result.get(
                "symbol"
            ),
            layer="L0",
            stack="chat_public",
            details={
                "operation": "local_model_inference",
                "provider": OLLAMA_PROVIDER,
                "model": runtime_result.get(
                    "model"
                ),
                "latency_ms": (
                    perf_counter()
                    - inference_started
                ) * 1000,
                "success": (
                    intent_status == "ok"
                ),
                "error": runtime_result.get(
                    "error"
                ),
            },
        )

    assistant_content = _response_message(
        runtime_result["response"]
    )

    if (
        retrieval_bundle.grounded
        and retrieval_bundle.citations
    ):
        assistant_content = (
            _ensure_approved_retrieval_citation(
                assistant_content,
                retrieval_bundle.citations,
            )
        )

        runtime_result[
            "response"
        ][
            "message"
        ] = assistant_content

    verification_started = perf_counter()

    verification_result: ResponseVerificationResult = (
        verify_response(
            assistant_content,
            math_bundle=math_bundle,
            retrieval_bundle=retrieval_bundle,
        )
    )

    assistant_content = (
        verification_result.final_response
    )

    runtime_result[
        "response_verification"
    ] = verification_result.as_dict()

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="RESPONSE_VERIFICATION_COMPLETED",
        node="response_verifier",
        source="model_runtime",
        destination="response_validation",
        status=(
            "completed"
            if verification_result.passed
            else (
                "repaired"
                if verification_result.repaired
                else "failed"
            )
        ),
        symbol=runtime_result.get(
            "symbol"
        ),
        layer="L3",
        stack="chat_public",
        details={
            "operation":
                "verify_generated_response",
            "verification_status":
                verification_result.status,
            "passed":
                verification_result.passed,
            "repaired":
                verification_result.repaired,
            "fail_closed":
                verification_result.fail_closed,
            "violation_count":
                len(
                    verification_result.violations
                ),
            "violation_codes": [
                violation.code
                for violation
                in verification_result.violations
            ],
            "checks":
                verification_result.checks,
            "latency_ms": (
                perf_counter()
                - verification_started
            ) * 1000,
        },
    )

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="RESPONSE_VALIDATED",
        node="response_validation",
        source=(
            "ollama_adapter"
            if runtime_result.get(
                "provider"
            )
            == OLLAMA_PROVIDER
            else "intent_classifier"
        ),
        destination="response_validation",
        status=(
            "completed"
            if intent_status == "ok"
            else intent_status
        ),
        symbol=runtime_result.get(
            "symbol"
        ),
        layer="L3",
        stack="chat_public",
        details={
            "operation": "response_validation",
            "response_bytes": len(
                assistant_content.encode(
                    "utf-8"
                )
            ),
            "success": (
                intent_status == "ok"
            ),
        },
    )

    assistant_persist_started = perf_counter()

    assistant_message = (
        await conversation_store.append_message(
            thread_id=thread.thread_id,
            parent_message_id=(
                user_message.message_id
            ),
            role="assistant",
            content=assistant_content,
            intent=runtime_result.get("intent"),
            symbol=runtime_result.get("symbol"),
            provider=runtime_result.get(
                "provider"
            ),
            model=runtime_result.get("model"),
            metadata={
                "response_type": (
                    runtime_result["response"]
                    .get("type")
                ),
                "strategy_capture": (
                    runtime_result.get(
                        "strategy_capture"
                    )
                ),
                "runtime_status": (
                    runtime_result.get("status")
                ),
                "cognitive_route": (
                    runtime_result.get(
                        "cognitive_route"
                    )
                ),
                "live_retrieval": {
                    "requested":
                        retrieval_bundle.requested,
                    "grounded":
                        retrieval_bundle.grounded,
                    "result_count":
                        len(
                            retrieval_bundle.results
                        ),
                    "citations":
                        list(
                            retrieval_bundle.citations
                        ),
                    "error":
                        retrieval_bundle.error,
                },
                "live_math": {
                    "requested":
                        math_bundle.requested,
                    "extracted":
                        math_bundle.extracted,
                    "grounded":
                        math_bundle.grounded,
                    "operation":
                        math_bundle.operation,
                    "arguments":
                        math_bundle.arguments,
                    "result":
                        math_bundle.result,
                    "error":
                        math_bundle.error,
                },
                "response_verification":
                    verification_result.as_dict(),
            },
        )
    )

    current_turn_evidence: list[
        ToolEvidence
    ] = []

    verification_evidence = ToolEvidence(
        thread_id=thread.thread_id,
        tool_name="response_verification",
        tool_call_id=trace_id,
        claim_types=[
            "response_consistency",
            "deterministic_math_consistency",
            "citation_validation",
            "paper_only_boundary",
        ],
        request={
            "assistant_message_id":
                assistant_message.message_id,
            "math_requested":
                math_bundle.requested,
            "retrieval_requested":
                retrieval_bundle.requested,
        },
        result={
            "status":
                verification_result.status,
            "passed":
                verification_result.passed,
            "repaired":
                verification_result.repaired,
            "fail_closed":
                verification_result.fail_closed,
            "checks":
                verification_result.checks,
            "violations": [
                violation.as_dict()
                for violation
                in verification_result.violations
            ],
        },
        status=(
            "success"
            if (
                verification_result.passed
                or verification_result.repaired
            )
            else "error"
        ),
        metadata={
            "assistant_message_id":
                assistant_message.message_id,
            "user_message_id":
                user_message.message_id,
            "runtime_trace_id":
                trace_id,
            "read_only":
                True,
            "deterministic":
                True,
            "pre_persistence_verification":
                True,
        },
    )

    await conversation_store.add_tool_evidence(
        verification_evidence
    )

    current_turn_evidence.append(
        verification_evidence
    )

    if math_bundle.requested:
        math_evidence = ToolEvidence(
            thread_id=thread.thread_id,
            tool_name=(
                "deterministic_math_engine"
            ),
            tool_call_id=trace_id,
            claim_types=[
                "deterministic_calculation",
                "exact_numeric_result",
            ],
            request={
                "message":
                    request.message,
                "operation":
                    math_bundle.operation,
                "arguments":
                    math_bundle.arguments,
            },
            result={
                "grounded":
                    math_bundle.grounded,
                "extracted":
                    math_bundle.extracted,
                "succeeded":
                    math_bundle.succeeded,
                "calculation":
                    math_bundle.result,
                "error":
                    math_bundle.error,
            },
            status=(
                "success"
                if math_bundle.grounded
                else (
                    "error"
                    if math_bundle.extracted
                    else "unavailable"
                )
            ),
            metadata={
                "assistant_message_id":
                    assistant_message.message_id,
                "user_message_id":
                    user_message.message_id,
                "runtime_trace_id":
                    trace_id,
                "read_only":
                    True,
                "deterministic":
                    True,
                "precision":
                    (
                        math_bundle.result
                        or {}
                    ).get(
                        "precision"
                    ),
            },
        )

        await conversation_store.add_tool_evidence(
            math_evidence
        )

        current_turn_evidence.append(
            math_evidence
        )

    if retrieval_bundle.requested:
        retrieval_evidence = ToolEvidence(
            thread_id=thread.thread_id,
            tool_name=(
                "local_knowledge_retrieval"
            ),
            tool_call_id=trace_id,
            claim_types=[
                "knowledge_retrieval",
                "source_citation",
            ],
            request={
                "query":
                    request.message,
                "top_k":
                    5,
                "minimum_score":
                    0.18,
            },
            result={
                "grounded":
                    retrieval_bundle.grounded,
                "result_count":
                    len(
                        retrieval_bundle.results
                    ),
                "citations":
                    list(
                        retrieval_bundle.citations
                    ),
                "error":
                    retrieval_bundle.error,
            },
            status=(
                "success"
                if retrieval_bundle.error is None
                else "error"
            ),
            metadata={
                "assistant_message_id":
                    assistant_message.message_id,
                "user_message_id":
                    user_message.message_id,
                "runtime_trace_id":
                    trace_id,
                "read_only":
                    True,
                "canonical_index": (
                    "runtime/cognitive_engine/rag/"
                    "neuro_knowledge_index.json"
                ),
                "untrusted_evidence":
                    True,
            },
        )

        await conversation_store.add_tool_evidence(
            retrieval_evidence
        )

        current_turn_evidence.append(
            retrieval_evidence
        )

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="ASSISTANT_MESSAGE_PERSISTED",
        node="postgresql_adapter",
        source="response_validation",
        destination="postgresql_adapter",
        status="completed",
        layer="L0",
        stack="db_runtime",
        details={
            "operation": "append_assistant_message",
            "latency_ms": (
                perf_counter()
                - assistant_persist_started
            ) * 1000,
            "response_bytes": len(
                assistant_content.encode(
                    "utf-8"
                )
            ),
            "success": True,
        },
    )

    memory_started = perf_counter()

    state = await update_summary_memory(
        thread_id=thread.thread_id,
        user_message=user_message,
        assistant_message=assistant_message,
        strategy_capture=runtime_result.get(
            "strategy_capture"
        ),
    )

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="SUMMARY_MEMORY_UPDATED",
        node="memory_context",
        source="postgresql_adapter",
        destination="memory_context",
        status="completed",
        layer="L2",
        stack="memory",
        details={
            "operation": "update_summary_memory",
            "latency_ms": (
                perf_counter()
                - memory_started
            ) * 1000,
            "success": True,
        },
    )

    response_status = str(
        runtime_result.get("status") or "ok"
    )

    if response_status not in {
        "ok",
        "error",
        "blocked",
    }:
        response_status = "error"

    response = ChatResponse(
        status=response_status,
        thread_id=thread.thread_id,
        user_message_id=user_message.message_id,
        assistant_message_id=(
            assistant_message.message_id
        ),
        message=assistant_content,
        intent=runtime_result.get("intent"),
        symbol=runtime_result.get("symbol"),
        provider=runtime_result.get("provider"),
        model=runtime_result.get("model"),
        tool_truth_state=runtime_result.get(
            "tool_truth_state",
            "not_required",
        ),
        conversation_state=state,
        error=runtime_result.get("error"),
        evidence=current_turn_evidence,
        metadata={
            "idempotent_replay": False,
            "streaming_enabled": False,
            "history_injected_into_model": True,
            "context_version": CONTEXT_VERSION,
            "context_recent_message_count": (
                assembled_context.recent_message_count
            ),
            "context_memory_count": (
                assembled_context.memory_count
            ),
            "context_evidence_count": (
                assembled_context.evidence_count
            ),
            "summary_memory_active": True,
            "strategy_capture": (
                runtime_result.get(
                    "strategy_capture"
                )
            ),
            "runtime_trace_id": trace_id,
            "retrieval_requested":
                retrieval_bundle.requested,
            "retrieval_grounded":
                retrieval_bundle.grounded,
            "retrieval_result_count":
                len(
                    retrieval_bundle.results
                ),
            "retrieval_citations":
                list(
                    retrieval_bundle.citations
                ),
            "retrieval_error":
                retrieval_bundle.error,
            "math_requested":
                math_bundle.requested,
            "math_extracted":
                math_bundle.extracted,
            "math_grounded":
                math_bundle.grounded,
            "math_operation":
                math_bundle.operation,
            "math_arguments":
                math_bundle.arguments,
            "math_result":
                math_bundle.result,
            "math_error":
                math_bundle.error,
            "verification_status":
                verification_result.status,
            "verification_passed":
                verification_result.passed,
            "verification_repaired":
                verification_result.repaired,
            "verification_fail_closed":
                verification_result.fail_closed,
            "verification_checks":
                verification_result.checks,
            "verification_violations": [
                violation.as_dict()
                for violation
                in verification_result.violations
            ],
        },
    )

    payload = response.model_dump(
        mode="json"
    )

    payload["response"] = runtime_result[
        "response"
    ]

    training_run = runtime_result.get(
        "training_run"
    )

    if isinstance(
        training_run,
        dict,
    ):
        payload["training_run"] = dict(
            training_run
        )

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="CHAT_RUNTIME_COMPLETED",
        node="chat_runtime",
        source="memory_context",
        destination="chat_runtime",
        status=(
            "completed"
            if response_status == "ok"
            else response_status
        ),
        symbol=runtime_result.get(
            "symbol"
        ),
        layer="L4",
        stack="chat_public",
        details={
            "operation": "run_chat_turn",
            "latency_ms": (
                perf_counter()
                - turn_started
            ) * 1000,
            "response_bytes": len(
                assistant_content.encode(
                    "utf-8"
                )
            ),
            "success": (
                response_status == "ok"
            ),
            "error": runtime_result.get(
                "error"
            ),
        },
    )

    return payload
