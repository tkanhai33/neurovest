#!/usr/bin/env python3

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
from typing import Any

from backend.app.stacks.chat_public.contracts import (
    ConversationState,
    MemoryFact,
    ToolEvidence,
)
from backend.app.stacks.chat_public.conversation_store import (
    conversation_store,
)
from backend.app.stacks.db_runtime import init_db


def print_result(result: dict[str, Any]) -> None:
    print(json.dumps(result, indent=2))


async def seed(thread_id: str) -> dict[str, Any]:
    await init_db()

    thread = await conversation_store.create_thread(
        thread_id=thread_id,
        title="134B6 restart persistence validation",
        metadata={
            "phase": "134B6_RESTART_PERSISTENCE_CERTIFICATION",
            "temporary": True,
            "created_by_process": "A",
        },
    )

    user_message = await conversation_store.append_message(
        thread_id=thread.thread_id,
        role="user",
        content="ATF means Adaptive Trend Follower.",
        client_message_id=f"{thread_id}-seed-user",
        intent="strategy_discussion",
        metadata={
            "validation_process": "A",
        },
    )

    assistant_message = await conversation_store.append_message(
        thread_id=thread.thread_id,
        parent_message_id=user_message.message_id,
        role="assistant",
        content=(
            "ATF is retained as Adaptive Trend Follower, "
            "a proposed strategy that has not yet been validated."
        ),
        provider="ollama",
        model="llama3.1",
        metadata={
            "validation_process": "A",
        },
    )

    state = ConversationState(
        thread_id=thread.thread_id,
        summary=(
            "The conversation defines ATF as Adaptive Trend "
            "Follower and marks it as proposed but not validated."
        ),
        active_strategy={
            "name": "Adaptive Trend Follower",
            "abbreviation": "ATF",
            "status": "proposed_not_validated",
        },
        portfolio_context={
            "value_cad": 300,
            "source": "user_statement",
        },
        remembered_terms={
            "ATF": "Adaptive Trend Follower",
        },
        last_message_id=assistant_message.message_id,
        metadata={
            "validation_process": "A",
        },
    )

    stored_state = await conversation_store.upsert_conversation_state(
        state
    )

    memory = await conversation_store.upsert_memory_fact(
        MemoryFact(
            thread_id=thread.thread_id,
            key="strategy.abbreviation.ATF",
            value={
                "name": "Adaptive Trend Follower",
                "status": "proposed_not_validated",
            },
            confidence=0.99,
            source_message_id=user_message.message_id,
            metadata={
                "validation_process": "A",
            },
        )
    )

    evidence = await conversation_store.add_tool_evidence(
        ToolEvidence(
            thread_id=thread.thread_id,
            tool_name="conversation_memory",
            tool_call_id=f"{thread_id}-evidence-call",
            claim_types=[
                "conversation_recall",
            ],
            request={
                "term": "ATF",
            },
            result={
                "meaning": "Adaptive Trend Follower",
            },
            status="success",
            metadata={
                "validation_process": "A",
            },
        )
    )

    recovered_thread = await conversation_store.require_thread(
        thread.thread_id
    )

    messages = await conversation_store.list_messages(
        thread.thread_id,
        limit=20,
        oldest_first=True,
    )

    result = {
        "process": "A",
        "operation": "seed",
        "thread_id": thread.thread_id,
        "user_message_id": user_message.message_id,
        "assistant_message_id": assistant_message.message_id,
        "memory_id": memory.memory_id,
        "evidence_id": evidence.evidence_id,
        "checks": {
            "thread_created": recovered_thread.thread_id == thread_id,
            "two_messages_persisted": len(messages) == 2,
            "message_count_is_two": recovered_thread.message_count == 2,
            "roles_ordered": [
                item.role for item in messages
            ] == ["user", "assistant"],
            "parent_link_persisted": (
                messages[1].parent_message_id
                == user_message.message_id
            ),
            "state_persisted": (
                stored_state.remembered_terms.get("ATF")
                == "Adaptive Trend Follower"
            ),
            "memory_persisted": (
                memory.key == "strategy.abbreviation.ATF"
            ),
            "evidence_persisted": (
                evidence.tool_name == "conversation_memory"
            ),
        },
    }

    result["passed"] = all(result["checks"].values())
    return result


async def recover_and_append(thread_id: str) -> dict[str, Any]:
    await init_db()

    thread = await conversation_store.require_thread(thread_id)

    original_messages = await conversation_store.list_messages(
        thread_id,
        limit=20,
        oldest_first=True,
    )

    state = await conversation_store.get_conversation_state(
        thread_id
    )

    memories = await conversation_store.list_memory_facts(
        thread_id
    )

    evidence = await conversation_store.list_tool_evidence(
        thread_id
    )

    bundle = await conversation_store.load_context_bundle(
        thread_id,
        message_limit=20,
        memory_limit=20,
        evidence_limit=20,
    )

    second_user = await conversation_store.append_message(
        thread_id=thread_id,
        parent_message_id=state.last_message_id,
        role="user",
        content="What did ATF stand for earlier?",
        client_message_id=f"{thread_id}-recover-user",
        intent="conversation_recall",
        metadata={
            "validation_process": "B",
        },
    )

    duplicate_second_user = await conversation_store.append_message(
        thread_id=thread_id,
        parent_message_id=state.last_message_id,
        role="user",
        content="This duplicate body must not create another row.",
        client_message_id=f"{thread_id}-recover-user",
        intent="conversation_recall",
        metadata={
            "validation_process": "B",
        },
    )

    second_assistant = await conversation_store.append_message(
        thread_id=thread_id,
        parent_message_id=second_user.message_id,
        role="assistant",
        content="ATF stood for Adaptive Trend Follower.",
        provider="ollama",
        model="llama3.1",
        metadata={
            "validation_process": "B",
        },
    )

    updated_state = ConversationState(
        thread_id=thread_id,
        summary=state.summary,
        active_entities=state.active_entities,
        active_strategy=state.active_strategy,
        portfolio_context=state.portfolio_context,
        pending_tasks=state.pending_tasks,
        remembered_terms=state.remembered_terms,
        last_message_id=second_assistant.message_id,
        metadata={
            **state.metadata,
            "last_recovered_by_process": "B",
        },
    )

    await conversation_store.upsert_conversation_state(
        updated_state
    )

    final_messages = await conversation_store.list_messages(
        thread_id,
        limit=20,
        oldest_first=True,
    )

    refreshed_thread = await conversation_store.require_thread(
        thread_id
    )

    result = {
        "process": "B",
        "operation": "recover_and_append",
        "thread_id": thread_id,
        "second_user_message_id": second_user.message_id,
        "second_assistant_message_id": second_assistant.message_id,
        "checks": {
            "thread_recovered_after_process_exit": (
                thread.thread_id == thread_id
            ),
            "original_two_messages_recovered": (
                len(original_messages) == 2
            ),
            "original_parent_link_recovered": (
                original_messages[1].parent_message_id
                == original_messages[0].message_id
            ),
            "state_recovered": (
                state.remembered_terms.get("ATF")
                == "Adaptive Trend Follower"
            ),
            "portfolio_context_recovered": (
                state.portfolio_context.get("value_cad") == 300
            ),
            "memory_recovered": (
                len(memories) == 1
                and memories[0].key
                == "strategy.abbreviation.ATF"
            ),
            "evidence_recovered": (
                len(evidence) == 1
                and evidence[0].tool_name
                == "conversation_memory"
            ),
            "context_bundle_recovered": (
                bundle["thread"].thread_id == thread_id
                and len(bundle["messages"]) == 2
                and len(bundle["memory_facts"]) == 1
                and len(bundle["tool_evidence"]) == 1
            ),
            "client_idempotency_survived_restart": (
                duplicate_second_user.message_id
                == second_user.message_id
            ),
            "only_two_new_messages_added": (
                len(final_messages) == 4
            ),
            "final_roles_ordered": (
                [item.role for item in final_messages]
                == [
                    "user",
                    "assistant",
                    "user",
                    "assistant",
                ]
            ),
            "second_turn_parent_chain_correct": (
                final_messages[2].parent_message_id
                == original_messages[1].message_id
                and final_messages[3].parent_message_id
                == final_messages[2].message_id
            ),
            "thread_message_count_is_four": (
                refreshed_thread.message_count == 4
            ),
        },
    }

    result["passed"] = all(result["checks"].values())
    return result


async def verify_final(thread_id: str) -> dict[str, Any]:
    await init_db()

    thread = await conversation_store.require_thread(
        thread_id
    )

    messages = await conversation_store.list_messages(
        thread_id,
        limit=20,
        oldest_first=True,
    )

    state = await conversation_store.get_conversation_state(
        thread_id
    )

    memories = await conversation_store.list_memory_facts(
        thread_id
    )

    evidence = await conversation_store.list_tool_evidence(
        thread_id
    )

    health = await conversation_store.healthcheck()

    timestamps = [
        message.created_at
        for message in messages
    ]

    result = {
        "process": "C",
        "operation": "verify_final",
        "thread_id": thread_id,
        "checks": {
            "thread_recovered_in_third_process": (
                thread.thread_id == thread_id
            ),
            "four_messages_durable": (
                len(messages) == 4
            ),
            "thread_count_durable": (
                thread.message_count == 4
            ),
            "message_order_durable": (
                [item.role for item in messages]
                == [
                    "user",
                    "assistant",
                    "user",
                    "assistant",
                ]
            ),
            "timestamps_ordered": (
                timestamps == sorted(timestamps)
            ),
            "first_parent_link_durable": (
                messages[1].parent_message_id
                == messages[0].message_id
            ),
            "second_user_parent_link_durable": (
                messages[2].parent_message_id
                == messages[1].message_id
            ),
            "second_assistant_parent_link_durable": (
                messages[3].parent_message_id
                == messages[2].message_id
            ),
            "conversation_state_durable": (
                state.remembered_terms.get("ATF")
                == "Adaptive Trend Follower"
            ),
            "last_message_pointer_durable": (
                state.last_message_id
                == messages[3].message_id
            ),
            "active_strategy_durable": (
                isinstance(state.active_strategy, dict)
                and state.active_strategy.get("abbreviation")
                == "ATF"
            ),
            "memory_durable": (
                len(memories) == 1
                and memories[0].value.get("name")
                == "Adaptive Trend Follower"
            ),
            "evidence_durable": (
                len(evidence) == 1
                and evidence[0].status == "success"
            ),
            "store_healthcheck_passed": (
                health.get("status") == "ok"
                and health.get("persistent") is True
            ),
        },
    }

    result["passed"] = all(result["checks"].values())
    return result


async def cleanup(thread_id: str) -> dict[str, Any]:
    await init_db()

    await conversation_store.delete_thread_for_testing(
        thread_id
    )

    thread = await conversation_store.get_thread(
        thread_id
    )

    result = {
        "process": "C",
        "operation": "cleanup",
        "thread_id": thread_id,
        "checks": {
            "temporary_thread_removed": (
                thread is None
            ),
        },
    }

    result["passed"] = all(result["checks"].values())
    return result


async def main() -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "operation",
        choices=[
            "seed",
            "recover",
            "verify",
            "cleanup",
        ],
    )

    parser.add_argument(
        "--thread-id",
        required=True,
    )

    arguments = parser.parse_args()

    if arguments.operation == "seed":
        result = await seed(
            arguments.thread_id
        )

    elif arguments.operation == "recover":
        result = await recover_and_append(
            arguments.thread_id
        )

    elif arguments.operation == "verify":
        result = await verify_final(
            arguments.thread_id
        )

    else:
        result = await cleanup(
            arguments.thread_id
        )

    print_result(result)

    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(
        asyncio.run(main())
    )
