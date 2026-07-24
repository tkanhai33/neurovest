#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import json

from backend.app.stacks.chat_public.contracts import (
    CHAT_CONTRACT_VERSION,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ChatThread,
    ConversationState,
    MemoryFact,
    ToolEvidence,
)


ROOT = Path(".").resolve()

FRONTEND_CONTRACT = (
    ROOT
    / "frontend/services/chat/chatContracts.ts"
)


def field_names(model_type) -> set[str]:
    fields = getattr(
        model_type,
        "model_fields",
        None,
    )

    if fields is None:
        fields = getattr(
            model_type,
            "__fields__",
            {},
        )

    return set(fields.keys())


thread = ChatThread(
    title="134A validation thread"
)

user_message = ChatMessage(
    thread_id=thread.thread_id,
    role="user",
    content="What did ATF mean earlier?",
)

assistant_message = ChatMessage(
    thread_id=thread.thread_id,
    parent_message_id=user_message.message_id,
    role="assistant",
    content="ATF referred to Adaptive Trend Follower.",
    provider="ollama",
    model="llama3.1",
)

memory = MemoryFact(
    thread_id=thread.thread_id,
    key="strategy.abbreviation.ATF",
    value="Adaptive Trend Follower",
    source_message_id=user_message.message_id,
)

evidence = ToolEvidence(
    thread_id=thread.thread_id,
    tool_name="conversation_memory",
    claim_types=["conversation_recall"],
    request={
        "term": "ATF",
    },
    result={
        "meaning": "Adaptive Trend Follower",
    },
    status="success",
)

state = ConversationState(
    thread_id=thread.thread_id,
    summary=(
        "The user discussed a proposed strategy named "
        "Adaptive Trend Follower, abbreviated ATF."
    ),
    active_strategy={
        "name": "Adaptive Trend Follower",
        "abbreviation": "ATF",
        "status": "proposed_not_validated",
    },
    remembered_terms={
        "ATF": "Adaptive Trend Follower",
    },
    last_message_id=assistant_message.message_id,
)

request = ChatRequest(
    message="Would ATF suit this portfolio?",
    thread_id=thread.thread_id,
    parent_message_id=assistant_message.message_id,
)

response = ChatResponse(
    status="ok",
    thread_id=thread.thread_id,
    user_message_id=user_message.message_id,
    assistant_message_id=assistant_message.message_id,
    message=(
        "ATF refers to the proposed Adaptive Trend "
        "Follower strategy."
    ),
    provider="ollama",
    model="llama3.1",
    tool_truth_state="grounded",
    evidence=[evidence],
    memory_updates=[memory],
    conversation_state=state,
)

frontend_text = FRONTEND_CONTRACT.read_text(
    encoding="utf-8"
)

checks = {
    "contract_version_correct": (
        CHAT_CONTRACT_VERSION == "134A.v1"
    ),
    "thread_has_thread_id": (
        "thread_id" in field_names(ChatThread)
    ),
    "message_has_parent": (
        "parent_message_id"
        in field_names(ChatMessage)
    ),
    "message_has_role": (
        "role" in field_names(ChatMessage)
    ),
    "state_has_summary": (
        "summary"
        in field_names(ConversationState)
    ),
    "state_has_remembered_terms": (
        "remembered_terms"
        in field_names(ConversationState)
    ),
    "memory_has_source_message": (
        "source_message_id"
        in field_names(MemoryFact)
    ),
    "evidence_has_tool_name": (
        "tool_name"
        in field_names(ToolEvidence)
    ),
    "request_accepts_thread": (
        request.thread_id == thread.thread_id
    ),
    "response_returns_thread": (
        response.thread_id == thread.thread_id
    ),
    "response_has_truth_state": (
        "tool_truth_state"
        in field_names(ChatResponse)
    ),
    "frontend_thread_contract_present": (
        "ChatThreadContract" in frontend_text
    ),
    "frontend_message_contract_present": (
        "ChatMessageContract" in frontend_text
    ),
    "frontend_state_contract_present": (
        "ConversationStateContract"
        in frontend_text
    ),
    "frontend_memory_contract_present": (
        "MemoryFactContract" in frontend_text
    ),
    "frontend_evidence_contract_present": (
        "ToolEvidenceContract" in frontend_text
    ),
    "frontend_request_contract_present": (
        "ThreadedChatRequest" in frontend_text
    ),
    "frontend_response_contract_present": (
        "ThreadedChatResponse" in frontend_text
    ),
    "streaming_not_enabled": (
        request.stream is False
    ),
}

certified = all(checks.values())

result = {
    "phase": (
        "134A_CHAT_THREAD_AND_MEMORY_CONTRACT"
    ),
    "version": CHAT_CONTRACT_VERSION,
    "checks": checks,
    "sample": {
        "thread_id": thread.thread_id,
        "user_message_id": user_message.message_id,
        "assistant_message_id": (
            assistant_message.message_id
        ),
        "remembered_term": (
            state.remembered_terms["ATF"]
        ),
        "tool_truth_state": (
            response.tool_truth_state
        ),
    },
    "behavior": {
        "storage_implemented": False,
        "ollama_context_changed": False,
        "streaming_enabled": False,
        "frontend_chat_behavior_changed": False,
        "broker_execution_changed": False,
    },
    "certified": certified,
    "recommended_next_phase": (
        "134B_PERSISTENT_CHAT_STORE"
        if certified
        else "134A_CHAT_CONTRACT_REPAIR"
    ),
}

out_dir = (
    ROOT
    / "runtime/chat_contracts"
)
out_dir.mkdir(
    parents=True,
    exist_ok=True,
)

out_json = (
    out_dir
    / "134A_chat_thread_and_memory_contract_latest.json"
)

out_txt = (
    out_dir
    / "134A_chat_thread_and_memory_contract_latest.txt"
)

out_json.write_text(
    json.dumps(
        result,
        indent=2,
    ),
    encoding="utf-8",
)

lines = [
    result["phase"],
    "",
    f"version: {result['version']}",
    f"certified: {certified}",
    "",
    "CHECKS",
]

for name, passed in checks.items():
    lines.append(
        f"{name}: {'PASS' if passed else 'FAIL'}"
    )

lines.extend(
    [
        "",
        "BEHAVIOR",
        "storage_implemented: False",
        "ollama_context_changed: False",
        "streaming_enabled: False",
        "frontend_chat_behavior_changed: False",
        "broker_execution_changed: False",
        "",
        (
            "next: "
            f"{result['recommended_next_phase']}"
        ),
    ]
)

out_txt.write_text(
    "\n".join(lines) + "\n",
    encoding="utf-8",
)

print(
    json.dumps(
        result,
        indent=2,
    )
)

if not certified:
    raise SystemExit(1)
