#!/usr/bin/env python3

from __future__ import annotations

import asyncio
from pathlib import Path
import ast
import json

from backend.app.stacks.chat_public.contracts import (
    ConversationState,
    MemoryFact,
    ToolEvidence,
)
from backend.app.stacks.chat_public.conversation_store import (
    conversation_store,
)
from backend.app.stacks.db_runtime import init_db


ROOT = Path(".").resolve()

PHASE = "134B3_CONVERSATION_STORE_IMPLEMENTATION"

STORE_FILE = (
    ROOT
    / "backend/app/stacks/chat_public/conversation_store.py"
)

OUT_DIR = ROOT / "runtime/chat_persistence"
OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUT_JSON = (
    OUT_DIR
    / "134B3_conversation_store_latest.json"
)

OUT_TXT = (
    OUT_DIR
    / "134B3_conversation_store_latest.txt"
)


async def validate() -> dict:
    store_text = STORE_FILE.read_text(
        encoding="utf-8"
    )

    ast.parse(store_text)

    static_checks = {
        "conversation_store_class_exists": (
            "class ConversationStore"
            in store_text
        ),
        "create_thread_exists": (
            "async def create_thread"
            in store_text
        ),
        "append_message_exists": (
            "async def append_message"
            in store_text
        ),
        "list_messages_exists": (
            "async def list_messages"
            in store_text
        ),
        "state_upsert_exists": (
            "async def upsert_conversation_state"
            in store_text
        ),
        "memory_upsert_exists": (
            "async def upsert_memory_fact"
            in store_text
        ),
        "evidence_store_exists": (
            "async def add_tool_evidence"
            in store_text
        ),
        "context_bundle_exists": (
            "async def load_context_bundle"
            in store_text
        ),
        "no_separate_engine": (
            "create_async_engine"
            not in store_text
        ),
        "canonical_session_used": (
            "from backend.app.stacks.db_runtime "
            "import async_session"
            in store_text
        ),
    }

    await init_db()

    thread = await conversation_store.create_thread(
        title="134B3 persistence validation",
        metadata={
            "phase": PHASE,
            "temporary": True,
        },
    )

    try:
        user_message = (
            await conversation_store.append_message(
                thread_id=thread.thread_id,
                role="user",
                content=(
                    "ATF means Adaptive Trend Follower."
                ),
                client_message_id=(
                    "134B3-validation-user-message"
                ),
                intent="strategy_discussion",
            )
        )

        duplicate_user_message = (
            await conversation_store.append_message(
                thread_id=thread.thread_id,
                role="user",
                content=(
                    "This duplicate should not be inserted."
                ),
                client_message_id=(
                    "134B3-validation-user-message"
                ),
                intent="strategy_discussion",
            )
        )

        assistant_message = (
            await conversation_store.append_message(
                thread_id=thread.thread_id,
                parent_message_id=(
                    user_message.message_id
                ),
                role="assistant",
                content=(
                    "I will retain ATF as Adaptive "
                    "Trend Follower."
                ),
                provider="ollama",
                model="llama3.1",
            )
        )

        state = ConversationState(
            thread_id=thread.thread_id,
            summary=(
                "ATF refers to Adaptive Trend Follower."
            ),
            active_strategy={
                "name": "Adaptive Trend Follower",
                "abbreviation": "ATF",
                "status": "proposed_not_validated",
            },
            portfolio_context={
                "value_cad": 300,
            },
            remembered_terms={
                "ATF": "Adaptive Trend Follower",
            },
            last_message_id=(
                assistant_message.message_id
            ),
        )

        stored_state = (
            await conversation_store
            .upsert_conversation_state(state)
        )

        first_memory = MemoryFact(
            thread_id=thread.thread_id,
            key="strategy.abbreviation.ATF",
            value="Adaptive Trend Follower",
            confidence=0.95,
            source_message_id=(
                user_message.message_id
            ),
        )

        await conversation_store.upsert_memory_fact(
            first_memory
        )

        updated_memory = MemoryFact(
            thread_id=thread.thread_id,
            key="strategy.abbreviation.ATF",
            value={
                "name": "Adaptive Trend Follower",
                "status": "proposed_not_validated",
            },
            confidence=0.99,
            source_message_id=(
                assistant_message.message_id
            ),
        )

        stored_memory = (
            await conversation_store
            .upsert_memory_fact(updated_memory)
        )

        evidence = ToolEvidence(
            thread_id=thread.thread_id,
            tool_name="conversation_store",
            tool_call_id="134B3-validation-call",
            claim_types=[
                "conversation_recall",
            ],
            request={
                "key": (
                    "strategy.abbreviation.ATF"
                ),
            },
            result={
                "meaning": (
                    "Adaptive Trend Follower"
                ),
            },
            status="success",
        )

        stored_evidence = (
            await conversation_store
            .add_tool_evidence(evidence)
        )

        recovered_thread = (
            await conversation_store.require_thread(
                thread.thread_id
            )
        )

        recovered_messages = (
            await conversation_store.list_messages(
                thread.thread_id,
                limit=20,
            )
        )

        recovered_state = (
            await conversation_store
            .get_conversation_state(
                thread.thread_id
            )
        )

        recovered_memories = (
            await conversation_store
            .list_memory_facts(
                thread.thread_id
            )
        )

        recovered_evidence = (
            await conversation_store
            .list_tool_evidence(
                thread.thread_id
            )
        )

        bundle = (
            await conversation_store
            .load_context_bundle(
                thread.thread_id
            )
        )

        health = (
            await conversation_store.healthcheck()
        )

        runtime_checks = {
            "thread_persisted": (
                recovered_thread.thread_id
                == thread.thread_id
            ),
            "thread_message_count_updated": (
                recovered_thread.message_count == 2
            ),
            "client_message_id_idempotent": (
                duplicate_user_message.message_id
                == user_message.message_id
            ),
            "duplicate_not_inserted": (
                len(recovered_messages) == 2
            ),
            "parent_message_preserved": (
                recovered_messages[1]
                .parent_message_id
                == user_message.message_id
            ),
            "message_roles_preserved": (
                [
                    message.role
                    for message in recovered_messages
                ]
                == ["user", "assistant"]
            ),
            "state_summary_persisted": (
                recovered_state.summary
                == stored_state.summary
            ),
            "remembered_term_persisted": (
                recovered_state.remembered_terms.get(
                    "ATF"
                )
                == "Adaptive Trend Follower"
            ),
            "portfolio_context_persisted": (
                recovered_state.portfolio_context.get(
                    "value_cad"
                )
                == 300
            ),
            "memory_upserted_without_duplicate": (
                len(recovered_memories) == 1
            ),
            "memory_value_updated": (
                stored_memory.value
                == {
                    "name": (
                        "Adaptive Trend Follower"
                    ),
                    "status": (
                        "proposed_not_validated"
                    ),
                }
            ),
            "tool_evidence_persisted": (
                len(recovered_evidence) == 1
                and recovered_evidence[0].evidence_id
                == stored_evidence.evidence_id
            ),
            "context_bundle_complete": (
                bundle["thread"].thread_id
                == thread.thread_id
                and len(bundle["messages"]) == 2
                and len(bundle["memory_facts"]) == 1
                and len(bundle["tool_evidence"]) == 1
            ),
            "healthcheck_passed": (
                health.get("status") == "ok"
                and health.get("persistent") is True
            ),
        }

        checks = {
            **static_checks,
            **runtime_checks,
        }

        certified = all(checks.values())

        return {
            "phase": PHASE,
            "checks": checks,
            "database_connection_attempted": True,
            "tables_created_or_verified": True,
            "temporary_thread_id": thread.thread_id,
            "temporary_user_message_id": (
                user_message.message_id
            ),
            "temporary_assistant_message_id": (
                assistant_message.message_id
            ),
            "message_count": len(
                recovered_messages
            ),
            "memory_count": len(
                recovered_memories
            ),
            "evidence_count": len(
                recovered_evidence
            ),
            "health": health,
            "behavior": {
                "live_chat_wired": False,
                "ollama_context_changed": False,
                "streaming_enabled": False,
                "broker_execution_changed": False,
                "temporary_records_cleaned": True,
            },
            "certified": certified,
            "recommended_next_phase": (
                "134B4_CHAT_API_THREAD_WIRING"
                if certified
                else (
                    "134B3_CONVERSATION_STORE_REPAIR"
                )
            ),
        }

    finally:
        await conversation_store.delete_thread_for_testing(
            thread.thread_id
        )


async def main() -> int:
    result = await validate()

    OUT_JSON.write_text(
        json.dumps(
            result,
            indent=2,
        ),
        encoding="utf-8",
    )

    lines = [
        result["phase"],
        "",
        f"certified: {result['certified']}",
        "",
        "CHECKS",
    ]

    for name, passed in result["checks"].items():
        lines.append(
            f"{name}: "
            f"{'PASS' if passed else 'FAIL'}"
        )

    lines.extend(
        [
            "",
            "PERSISTENCE",
            "database_connection_attempted: True",
            "tables_created_or_verified: True",
            (
                "message_count: "
                f"{result['message_count']}"
            ),
            (
                "memory_count: "
                f"{result['memory_count']}"
            ),
            (
                "evidence_count: "
                f"{result['evidence_count']}"
            ),
            "temporary_records_cleaned: True",
            "",
            "BEHAVIOR",
            "live_chat_wired: False",
            "ollama_context_changed: False",
            "streaming_enabled: False",
            "broker_execution_changed: False",
            "",
            (
                "next: "
                f"{result['recommended_next_phase']}"
            ),
        ]
    )

    OUT_TXT.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            result,
            indent=2,
        )
    )

    return 0 if result["certified"] else 1


if __name__ == "__main__":
    raise SystemExit(
        asyncio.run(main())
    )
